import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from adafruit_servokit import ServoKit
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')

# ==============================
# CONFIGURACIÓN SERVOS
# ==============================
kit = ServoKit(channels=16)
for ch in range(6):
    kit.servo[ch].set_pulse_width_range(500, 2500)

servo_config = {
    0: {"offset": 0,  "invert": False},
    1: {"offset": 0,  "invert": False},
    2: {"offset": 0,  "invert": True},
    3: {"offset": 0,  "invert": False},
    4: {"offset": 0,  "invert": False},
    5: {"offset": 0,  "invert": False},
}

# ==============================
# MODELO DEL ROBOT
# ==============================
L1, L2, L3 = 5, 5, 5
links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),
    RevoluteDH(d=0, a=L1, alpha=0),
    RevoluteDH(d=0, a=L2, alpha=0),
    RevoluteDH(d=0, a=L3, alpha=0)
]
robot = DHRobot(links, name="Robot_4R")

# ==============================
# INTERFAZ
# ==============================
class ServoControl(QWidget):
    def __init__(self):
        super().__init__()
        self.angles = [90, 90, 90, 90]  # Posición inicial
        self.initUI()

        # Dibujar robot 3D bonito usando robot.plot()
        self.robot_fig = robot.plot(np.deg2rad(self.angles), block=False)

    def initUI(self):
        layout = QVBoxLayout()
        self.labels = []
        self.sliders = []

        for i in range(4):
            lbl = QLabel(f"Articulación {i+1}: 90°", self)
            sld = QSlider(Qt.Horizontal, self)
            sld.setMinimum(0)
            sld.setMaximum(180)
            sld.setValue(90)
            sld.valueChanged.connect(lambda val, idx=i: self.move_servo(idx, val))
            layout.addWidget(lbl)
            layout.addWidget(sld)
            self.labels.append(lbl)
            self.sliders.append(sld)

        self.pos_label = QLabel("Posición final: (x, y, z)", self)
        layout.addWidget(self.pos_label)
        self.setLayout(layout)
        self.setWindowTitle("Control Robot 4R - Simulación + PCA9685")
        self.setGeometry(200, 200, 400, 300)

    def move_servo(self, index, angle):
        self.angles[index] = angle
        # Control servos reales
        self.set_servo_angle(index, angle)
        # Actualizar label
        self.labels[index].setText(f"Articulación {index+1}: {angle}°")
        # Actualizar posición efector final
        pos = self.forward_kinematics(*self.angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
        # Actualizar simulación 3D
        self.update_simulation()

    def set_servo_angle(self, channel, angle):
        cfg = servo_config[channel]
        offset, invert = cfg["offset"], cfg["invert"]
        adj_angle = angle + offset
        if invert:
            adj_angle = 180 - adj_angle
        adj_angle = max(0, min(180, adj_angle))
        kit.servo[channel].angle = adj_angle

    def forward_kinematics(self, theta1, theta2, theta3, theta4):
        """Devuelve posición del efector final."""
        def dh_matrix(theta, d, a, alpha):
            theta = np.deg2rad(theta)
            alpha = np.deg2rad(alpha)
            return np.array([
                [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
                [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
                [0,              np.sin(alpha),               np.cos(alpha),               d],
                [0, 0, 0, 1]
            ])
        T1 = dh_matrix(theta1, 0, 0, 90)
        T2 = dh_matrix(theta2, 0, L1, 0)
        T3 = dh_matrix(theta3, 0, L2, 0)
        T4 = dh_matrix(theta4, 0, L3, 0)
        T = T1 @ T2 @ T3 @ T4
        return T[:3, 3]

    def update_simulation(self):
        # Usar robot.plot() en block=False para actualizar la figura 3D original
        robot.plot(np.deg2rad(self.angles), block=False)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
