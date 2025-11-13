import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from adafruit_servokit import ServoKit
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

# ==============================
# CONFIGURACIÓN PCA9685 Y SERVOS
# ==============================

kit = ServoKit(channels=16)
for ch in range(6):
    kit.servo[ch].set_pulse_width_range(500, 2500)

servo_config = {
    0: {"offset": 0,  "invert": False},   # Base
    1: {"offset": 0,  "invert": False},   # Hombro A
    2: {"offset": 0,  "invert": True},    # Hombro B
    3: {"offset": 0,  "invert": False},   # Codo
    4: {"offset": 0,  "invert": False},   # Muñeca
    5: {"offset": 0,  "invert": False},   # Pinza
}

# Longitudes de eslabones
L1, L2, L3 = 5, 5, 5

# ==============================
# MODELO DEL ROBOT
# ==============================

links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),  # Base
    RevoluteDH(d=0, a=L1, alpha=0),              # Hombro
    RevoluteDH(d=0, a=L2, alpha=0),              # Codo
    RevoluteDH(d=0, a=L3, alpha=0)               # Muñeca
]
robot = DHRobot(links, name="Robot_4R")

# ==============================
# INTERFAZ GRÁFICA
# ==============================

class ServoControl(QWidget):
    def __init__(self):
        super().__init__()
        self.angles = [90, 90, 90, 90]  # Posición inicial
        self.initUI()

        # Crear figura 3D interactiva
        self.fig = plt.figure("Simulación 3D del Robot", figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        plt.ion()
        self.fig.show()

        # Dibujo inicial
        self.update_simulation()

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

        # Actualizar posición mostrada
        pos = self.forward_kinematics(*self.angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

        # Actualizar simulación
        self.update_simulation()

    def set_servo_angle(self, channel, angle):
        cfg = servo_config[channel]
        offset, invert = cfg["offset"], cfg["invert"]
        adj_angle = angle + offset
        adj_angle = max(0, min(180, adj_angle))
        if invert:
            adj_angle = 180 - adj_angle
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
                [0,              0,                           0,                           1]
            ])
        T1 = dh_matrix(theta1, 0, 0, 90)
        T2 = dh_matrix(theta2, 0, L1, 0)
        T3 = dh_matrix(theta3, 0, L2, 0)
        T4 = dh_matrix(theta4, 0, L3, 0)
        T = T1 @ T2 @ T3 @ T4
        return T[:3, 3]

    def draw_cylinder(self, p1, p2, radius=0.3, color='steelblue'):
        """Dibuja un cilindro 3D entre dos puntos."""
        v = p2 - p1
        mag = np.linalg.norm(v)
        if mag == 0:
            return
        v = v / mag

        # Crear un sistema de coordenadas local
        not_v = np.array([1, 0, 0]) if (abs(v[0]) < 0.99) else np.array([0, 1, 0])
        n1 = np.cross(v, not_v)
        n1 /= np.linalg.norm(n1)
        n2 = np.cross(v, n1)

        # Superficie cilíndrica
        t = np.linspace(0, mag, 10)
        theta = np.linspace(0, 2 * np.pi, 20)
        t, theta = np.meshgrid(t, theta)

        X, Y, Z = [p1[i] + v[i]*t + radius*np.sin(theta)*n1[i] + radius*np.cos(theta)*n2[i] for i in range(3)]
        self.ax.plot_surface(X, Y, Z, color=color, alpha=0.8, linewidth=0, shade=True)

    def draw_sphere(self, center, radius=0.5, color='orange'):
        """Dibuja una esfera 3D pequeña en una articulación."""
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = center[0] + radius * np.cos(u) * np.sin(v)
        y = center[1] + radius * np.sin(u) * np.sin(v)
        z = center[2] + radius * np.cos(v)
        self.ax.plot_surface(x, y, z, color=color, shade=True)

    def update_simulation(self):
        """Dibuja el robot con estilo 3D."""
        q = np.deg2rad(self.angles)
        points = np.array([[0, 0, 0]])

        def fk_partial(thetas):
            T = np.eye(4)
            for i, th in enumerate(thetas):
                link = robot.links[i]
                A = link.A(th).A
                T = T @ A
            return T[:3, 3]

        for i in range(1, 5):
            p = fk_partial(q[:i])
            points = np.vstack((points, p))

        # Redibujar figura
        self.ax.cla()
        for i in range(len(points)-1):
            self.draw_cylinder(points[i], points[i+1])
        for p in points:
            self.draw_sphere(p)

        self.ax.set_xlim([-20, 20])
        self.ax.set_ylim([-20, 20])
        self.ax.set_zlim([0, 25])
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_box_aspect([1, 1, 1])
        self.ax.set_title("Simulación 3D del Robot (Mejorada)")
        self.ax.view_init(elev=25, azim=45)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
