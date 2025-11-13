import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from adafruit_servokit import ServoKit
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')  # Forzar backend compatible con PyQt5
import matplotlib.pyplot as plt
from roboticstoolbox.backends.PyPlot import PyPlot


# ==============================
# CONFIGURACIÓN PCA9685 Y SERVOS
# ==============================

kit = ServoKit(channels=16)

for ch in range(5):
    kit.servo[ch].set_pulse_width_range(500, 2500)

servo_config = {
    0: {"offset": 0,  "invert": False},   # Base (canal 0)
    1: {"offset": 0,  "invert": False},   # Hombro A (canal 1)
    2: {"offset": 0,  "invert": True},    # Hombro B (canal 2)
    3: {"offset": 0,  "invert": False},   # Codo (canal 3)
    4: {"offset": 0,  "invert": False},   # Muñeca (canal 4)
}

L1, L2, L3 = 5, 5, 5


# ==============================
# CREACIÓN DEL ROBOT SIMULADO
# ==============================

links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),  # Base
    RevoluteDH(d=0, a=L1, alpha=0),              # Hombro
    RevoluteDH(d=0, a=L2, alpha=0),              # Codo
    RevoluteDH(d=0, a=L3, alpha=0)               # Muñeca
]
robot = DHRobot(links, name="Robot_4R")

# Crear backend de simulación
env = PyPlot()
env.launch(name="Simulación Robot 4R")
env.add(robot, readonly=True)
robot.q = np.deg2rad([0, 0, 0, 0])
env.step(robot.q)
plt.show(block=False)


# ==============================
# FUNCIONES DE CINEMÁTICA
# ==============================

def dh_matrix(theta, d, a, alpha):
    theta = np.deg2rad(theta)
    alpha = np.deg2rad(alpha)
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),               np.cos(alpha),               d],
        [0,              0,                           0,                           1]
    ])

def forward_kinematics(theta1, theta2, theta3, theta4):
    T1 = dh_matrix(theta1, 0, 0, 90)
    T2 = dh_matrix(theta2, 0, L1, 0)
    T3 = dh_matrix(theta3, 0, L2, 0)
    T4 = dh_matrix(theta4, 0, L3, 0)
    T = T1 @ T2 @ T3 @ T4
    return T[:3, 3]


# ==============================
# INTERFAZ GRÁFICA (PyQt5)
# ==============================

class ServoControl(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.angles = [0, 0, 0, 0]  # iniciar en 0°

        # Temporizador para actualizar simulación
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)

    def initUI(self):
        layout = QVBoxLayout()
        self.labels = []
        self.sliders = []

        for i in range(4):
            lbl = QLabel(f"Articulación {i+1}: 0°", self)
            sld = QSlider(Qt.Horizontal, self)
            sld.setMinimum(0)
            sld.setMaximum(180)
            sld.setValue(0)
            sld.valueChanged.connect(lambda val, idx=i: self.move_servo(idx, val))
            layout.addWidget(lbl)
            layout.addWidget(sld)
            self.labels.append(lbl)
            self.sliders.append(sld)

        self.pos_label = QLabel("Posición final: (x, y, z)", self)
        layout.addWidget(self.pos_label)

        self.setLayout(layout)
        self.setWindowTitle("Control de Robot 4R - Simulación + PCA9685")
        self.setGeometry(200, 200, 400, 300)

    def move_servo(self, index, angle):
        """Mueve los servos físicos y actualiza los valores"""
        self.angles[index] = angle

        # Control de servos reales
        if index == 0:
            self.set_servo_angle(0, angle)
        elif index == 1:
            self.set_servo_angle(1, angle)
            self.set_servo_angle(2, angle)
        elif index == 2:
            self.set_servo_angle(3, angle)
        elif index == 3:
            self.set_servo_angle(4, angle)

        self.labels[index].setText(f"Articulación {index+1}: {angle}°")

        pos = forward_kinematics(*self.angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    def set_servo_angle(self, channel, angle):
        """Aplica offset e inversión antes de mover servo físico"""
        cfg = servo_config[channel]
        offset, invert = cfg["offset"], cfg["invert"]

        adj_angle = angle + offset
        adj_angle = max(0, min(180, adj_angle))
        if invert:
            adj_angle = 180 - adj_angle

        kit.servo[channel].angle = adj_angle

    def update_simulation(self):
        """Actualiza la simulación del robot"""
        q_rad = np.deg2rad(self.angles)
        robot.q = q_rad
        env.step(q_rad)  # ya no usa 'block'
        plt.pause(0.001)


# ==============================
# PROGRAMA PRINCIPAL
# ==============================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
