import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from adafruit_servokit import ServoKit
from roboticstoolbox import DHRobot, RevoluteDH
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

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

# Longitudes de eslabones
L1, L2, L3 = 5, 5, 5

# ==============================
# MODELO DEL ROBOT
# ==============================
links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),  # Base
    RevoluteDH(d=0, a=L1, alpha=0),             # Hombro
    RevoluteDH(d=0, a=L2, alpha=0),             # Codo
    RevoluteDH(d=0, a=L3, alpha=0)              # Muñeca
]
robot = DHRobot(links, name="Robot_4R")

# ==============================
# INTERFAZ GRÁFICA
# ==============================
class ServoControl(QWidget):
    def __init__(self):
        super().__init__()

        # Posición inicial en 0°
        self.angles = [0, 0, 0, 0]
        self.initUI()

        # Timer para actualizar la simulación
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)  # 20 FPS aprox

    def initUI(self):
        main_layout = QVBoxLayout()

        # Sliders para las articulaciones
        self.labels = []
        self.sliders = []
        for i in range(4):
            lbl = QLabel(f"Articulación {i+1}: 0°", self)
            sld = QSlider(Qt.Horizontal, self)
            sld.setMinimum(0)
            sld.setMaximum(180)
            sld.setValue(0)
            sld.valueChanged.connect(lambda val, idx=i: self.move_servo(idx, val))
            main_layout.addWidget(lbl)
            main_layout.addWidget(sld)
            self.labels.append(lbl)
            self.sliders.append(sld)

        # Botones Pick y Place para el servo de la pinza (canal 5)
        btn_layout = QHBoxLayout()
        pick_btn = QPushButton("Pick", self)
        pick_btn.clicked.connect(lambda: self.set_pinza(0))
        place_btn = QPushButton("Place", self)
        place_btn.clicked.connect(lambda: self.set_pinza(180))
        btn_layout.addWidget(pick_btn)
        btn_layout.addWidget(place_btn)
        main_layout.addLayout(btn_layout)

        # Label posición final
        self.pos_label = QLabel("Posición final: (x, y, z)", self)
        main_layout.addWidget(self.pos_label)

        # Canvas de Matplotlib embebido
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlim(-20, 20)
        self.ax.set_ylim(-20, 20)
        self.ax.set_zlim(0, 25)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")

        self.setLayout(main_layout)
        self.setWindowTitle("Control Robot 4R - Simulación + PCA9685")
        self.setGeometry(200, 200, 600, 600)

    def move_servo(self, index, angle):
        self.angles[index] = angle
        # Mover servos físicos
        if index == 0:
            self.set_servo_angle(0, angle)
        elif index == 1:
            self.set_servo_angle(1, angle)
            self.set_servo_angle(2, angle)
        elif index == 2:
            self.set_servo_angle(3, angle)
        elif index == 3:
            self.set_servo_angle(4, angle)

        # Actualizar label de ángulo
        self.labels[index].setText(f"Articulación {index+1}: {angle}°")
        # Actualizar posición final
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

    def set_pinza(self, angle):
        # Mover servo de la pinza (canal 5)
        self.set_servo_angle(5, angle)

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

    def update_simulation(self):
        self.ax.cla()  # limpiar la figura
        self.ax.set_xlim(-20, 20)
        self.ax.set_ylim(-20, 20)
        self.ax.set_zlim(0, 25)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        q_rad = np.deg2rad(self.angles)
        robot.plot(q_rad, block=False, ax=self.ax)
        self.canvas.draw()


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
