import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from adafruit_servokit import ServoKit
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')  # Usar backend compatible con PyQt5
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ==============================
# CONFIGURACIÓN PCA9685 Y SERVOS
# ==============================

kit = ServoKit(channels=16)

# Configurar el rango PWM de los servos
for ch in range(6):
    kit.servo[ch].set_pulse_width_range(500, 2500)

# Configuración por canal
servo_config = {
    0: {"offset": 0,  "invert": False},  # Base (rotación)
    1: {"offset": 0,  "invert": False},  # Hombro A
    2: {"offset": 0,  "invert": True},   # Hombro B (sincronizado)
    3: {"offset": 0,  "invert": False},  # Codo
    4: {"offset": 0,  "invert": False},  # Muñeca
    5: {"offset": 0,  "invert": False},  # Actuador (gripper)
}

# Longitudes de eslabones
L1, L2, L3 = 5, 5, 5

# ==============================
# CREACIÓN DEL ROBOT SIMULADO
# ==============================

links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),  # θ1
    RevoluteDH(d=0, a=L1, alpha=0),              # θ2
    RevoluteDH(d=0, a=L2, alpha=0),              # θ3
    RevoluteDH(d=0, a=L3, alpha=0)               # θ4
]
robot = DHRobot(links, name="Robot_4R")

# ==============================
# FUNCIONES DE CINEMÁTICA
# ==============================

def dh_matrix(theta, d, a, alpha):
    """Genera una matriz DH individual"""
    theta = np.deg2rad(theta)
    alpha = np.deg2rad(alpha)
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),               np.cos(alpha),               d],
        [0,              0,                           0,                           1]
    ])

def forward_kinematics(theta1, theta2, theta3, theta4):
    """Calcula posición final del efector"""
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
        self.angles = [0, 0, 0, 0]

        # Crear figura 3D
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.ion()
        plt.show(block=False)

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
        """Mueve servos físicos y actualiza la simulación"""
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

        self.labels[index].setText(f"Articulación {index+1}: {angle}°")

        pos = forward_kinematics(*self.angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    def set_servo_angle(self, channel, angle):
        """Configura el ángulo del servo real"""
        cfg = servo_config[channel]
        offset, invert = cfg["offset"], cfg["invert"]

        adj_angle = angle + offset
        adj_angle = max(0, min(180, adj_angle))
        if invert:
            adj_angle = 180 - adj_angle

        kit.servo[channel].angle = adj_angle

    def update_simulation(self):
        """Dibuja el robot 4R en la misma figura sin abrir ventanas nuevas"""
        q_rad = np.deg2rad(self.angles)

        self.ax.clear()
        self.ax.set_xlim([-20, 20])
        self.ax.set_ylim([-20, 20])
        self.ax.set_zlim([0, 25])
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_title("Simulación del Robot 4R")

        points = np.array([[0, 0, 0]])
        T = np.eye(4)
        a_vals = [0, L1, L2, L3]

        for i, q in enumerate(q_rad):
            T = T @ np.array([
                [np.cos(q), -np.sin(q), 0, a_vals[i] * np.cos(q)],
                [np.sin(q),  np.cos(q), 0, a_vals[i] * np.sin(q)],
                [0,          0,          1, 0],
                [0,          0,          0, 1]
            ])
            points = np.vstack((points, T[:3, 3]))

        self.ax.plot(points[:, 0], points[:, 1], points[:, 2], '-o', linewidth=2)
        plt.draw()
        plt.pause(0.001)


# ==============================
# PROGRAMA PRINCIPAL
# ==============================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
