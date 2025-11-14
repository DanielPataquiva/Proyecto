import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from adafruit_servokit import ServoKit
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

# Sensores
from sensor import Ultrasonico

# Intentamos importar la clase de simulación con compatibilidad:
# Si simulacion.py define RobotSimulation la usamos; si define Simulacion (nombre viejo), la renombramos.
try:
    from simulacion import RobotSimulation as SimClass
except Exception:
    try:
        from simulacion import Simulacion as SimClass
    except Exception:
        raise ImportError("No se pudo importar la clase de simulación desde simulacion.py. "
                          "Asegúrate de que exista RobotSimulation o Simulacion en ese archivo.")

# ==============================
# CONFIGURACIÓN PCA9685 Y SERVOS
# ==============================
kit = ServoKit(channels=16)
for ch in range(6):
    kit.servo[ch].set_pulse_width_range(500, 2500)

servo_config = {
    0: {"offset": 0, "invert": False},  # Base
    1: {"offset": 0, "invert": False},  # Hombro A
    2: {"offset": 0, "invert": True},   # Hombro B
    3: {"offset": 0, "invert": False},  # Codo
    4: {"offset": 0, "invert": False},  # Muñeca
    5: {"offset": 0, "invert": False},  # Pinza
}

# Longitudes de eslabones (definidas también en simulacion.py si es necesario)
L1, L2, L3 = 9, 9, 9

# ==============================
# INTERFAZ GRÁFICA
# ==============================
class ServoControl(QWidget):
    def __init__(self):
        super().__init__()

        self.angles = [0, 0, 0, 0]

        # Sensores (PINES REALES)
        self.sensor_lento = Ultrasonico(trigger=17, echo=27)   # modo lento
        self.sensor_parada = Ultrasonico(trigger=23, echo=24)  # parada total

        self.robot_lento = False
        self.robot_parado = False

        # Creamos el objeto de simulación (mantiene la figura y el eje)
        self.sim = SimClass()

        self.initUI()
        # mostramos primera posición en la simulación
        self.update_simulation()

        # Timer simulación
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)

        # Timer sensores
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.check_sensors)
        self.sensor_timer.start(200)

    def initUI(self):
        layout = QVBoxLayout()

        self.labels = []
        self.sliders = []

        self.nombres = ["Base", "Hombro", "Codo", "Muñeca"]

        for i in range(4):
            lbl = QLabel(f"{self.nombres[i]}: 0°", self)
            sld = QSlider(Qt.Horizontal, self)
            sld.setMinimum(0)
            sld.setMaximum(180)
            sld.setValue(0)
            sld.valueChanged.connect(lambda val, idx=i: self.move_servo(idx, val))

            layout.addWidget(lbl)
            layout.addWidget(sld)

            self.labels.append(lbl)
            self.sliders.append(sld)

        # Posición final
        self.pos_label = QLabel("Posición final: (x, y, z)", self)
        layout.addWidget(self.pos_label)

        # Sensores estado
        self.sensor_label = QLabel("Estado sensores: Normal", self)
        layout.addWidget(self.sensor_label)

        # Botones Pick y Place
        btn_layout = QHBoxLayout()
        self.pick_btn = QPushButton("Pick", self)
        self.pick_btn.clicked.connect(self.pick)
        self.place_btn = QPushButton("Place", self)
        self.place_btn.clicked.connect(self.place)
        btn_layout.addWidget(self.pick_btn)
        btn_layout.addWidget(self.place_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setWindowTitle("Control Robot 4R - Modo manual")
        self.setGeometry(200, 200, 400, 300)

    # ====================================
    # CHECK SENSORES
    # ====================================
    def check_sensors(self):
        try:
            dist_lento = self.sensor_lento.medir()
            dist_parada = self.sensor_parada.medir()
        except Exception as e:
            # Si hay error leyendo sensores, no bloqueamos la UI, solo avisamos por consola
            print("Error leyendo sensores:", e)
            return

        # Parada total
        if dist_parada < 10:
            self.robot_parado = True
            self.sensor_label.setText("Estado sensores: 🔴 DETENIDO (<10 cm)")
        else:
            self.robot_parado = False

        # Modo lento
        if dist_lento < 10:
            self.robot_lento = True
            if not self.robot_parado:
                self.sensor_label.setText("Estado sensores: 🟡 MODO LENTO (<10 cm)")
        else:
            self.robot_lento = False
            if not self.robot_parado:
                self.sensor_label.setText("Estado sensores: 🟢 Normal")

    # ====================================
    # CONTROL DE SERVOS
    # ====================================
    def move_servo(self, index, angle):
        # Parada total
        if self.robot_parado:
            print("⛔ Robot detenido por sensores")
            return

        # Modo lento
        if self.robot_lento:
            time.sleep(0.05)

        # Guardar y aplicar ángulo
        self.angles[index] = angle

        if index == 0:
            self.set_servo_angle(0, angle)
        elif index == 1:
            self.set_servo_angle(1, angle)
            self.set_servo_angle(2, angle)
        elif index == 2:
            self.set_servo_angle(3, angle)
        elif index == 3:
            self.set_servo_angle(4, angle)

        # Actualizar label
        self.labels[index].setText(f"{self.nombres[index]}: {angle}°")

        # Actualizar posición final (cinemática directa)
        pos = self.forward_kinematics(*self.angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    def set_servo_angle(self, channel, angle):
        cfg = servo_config[channel]
        offset, invert = cfg["offset"], cfg["invert"]
        adj_angle = angle + offset
        adj_angle = max(0, min(180, adj_angle))
        if invert:
            adj_angle = 180 - adj_angle
        kit.servo[channel].angle = adj_angle

    # ====================================
    # PICK Y PLACE
    # ====================================
    def pick(self):
        self.set_servo_angle(5, 0)

    def place(self):
        self.set_servo_angle(5, 180)

    # ====================================
    # CINEMÁTICA DIRECTA
    # ====================================
    def forward_kinematics(self, theta1, theta2, theta3, theta4):
        def dh_matrix(theta, d, a, alpha):
            theta = np.deg2rad(theta)
            alpha = np.deg2rad(alpha)
            return np.array([
                [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
                [np.sin(theta), np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
                [0, np.sin(alpha), np.cos(alpha), d],
                [0, 0, 0, 1]
            ])
        T1 = dh_matrix(theta1, 0, 0, 90)
        T2 = dh_matrix(theta2, 0, L1, 0)
        T3 = dh_matrix(theta3, 0, L2, 0)
        T4 = dh_matrix(theta4, 0, L3, 0)
        T = T1 @ T2 @ T3 @ T4
        return T[:3, 3]

    # ====================================
    # SIMULACIÓN (usa la clase de simulación importada)
    # ====================================
    def update_simulation(self):
        # Delegamos la actualización de la vista a la clase de simulación
        try:
            self.sim.update(self.angles)
        except Exception as e:
            print("Error actualizando simulación:", e)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
