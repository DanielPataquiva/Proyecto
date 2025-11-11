import sys
import math
import numpy as np
from PyQt5 import QtWidgets, QtCore
from robot import Robot
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot 2R - Simulación y Control Físico")
        self.setGeometry(200, 100, 1000, 600)

        # --- Robot físico ---
        self.robot = Robot()

        # --- Robot simulado ---
        L1, L2 = 10, 10
        self.robot_model = DHRobot([
            RevoluteDH(a=L1, alpha=0, d=0, offset=0),
            RevoluteDH(a=L2, alpha=0, d=0, offset=0)
        ], name="Robot 2R")

        # --- Layout principal ---
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # --- Panel izquierdo (controles) ---
        controls_layout = QtWidgets.QVBoxLayout()

        self.label1 = QtWidgets.QLabel("Articulación 1: 0°")
        self.slider1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider1.setRange(0, 180)
        self.slider1.setValue(0)

        self.label2 = QtWidgets.QLabel("Articulación 2: 0°")
        self.slider2 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider2.setRange(0, 180)
        self.slider2.setValue(0)

        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)

        controls_layout.addWidget(self.label1)
        controls_layout.addWidget(self.slider1)
        controls_layout.addWidget(self.label2)
        controls_layout.addWidget(self.slider2)
        controls_layout.addWidget(QtWidgets.QLabel("Lectura de ángulos (°):"))
        controls_layout.addWidget(self.output_text)
        controls_layout.addStretch()

        # --- Panel derecho (simulación 3D) ---
        sim_layout = QtWidgets.QVBoxLayout()
        self.fig = Figure(figsize=(6, 5))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvas(self.fig)
        sim_layout.addWidget(self.canvas)

        # Unir layouts
        main_layout.addLayout(controls_layout, 2)
        main_layout.addLayout(sim_layout, 3)

        # --- Conexión de sliders ---
        self.slider1.valueChanged.connect(self.actualizar_robot)
        self.slider2.valueChanged.connect(self.actualizar_robot)

        # --- Inicialización ---
        self.actualizar_robot()

    def actualizar_robot(self):
        ang1 = self.slider1.value()
        ang2 = self.slider2.value()

        # Actualiza labels
        self.label1.setText(f"Articulación 1: {ang1}°")
        self.label2.setText(f"Articulación 2: {ang2}°")

        # Mueve servos reales
        self.robot.mover_servos(ang1, ang2)

        # Escribe en GUI
        self.output_text.append(f"Art1: {ang1}° | Art2: {ang2}°")

        # Actualiza simulación 3D
        self.dibujar_robot([math.radians(ang1), math.radians(ang2)])

    def dibujar_robot(self, q):
        self.ax.clear()
        self.ax.set_title("Simulación 3D - Robot 2R")
        self.ax.set_xlim(-20, 20)
        self.ax.set_ylim(-20, 20)
        self.ax.set_zlim(-1, 20)
        self.ax.set_xlabel("X (cm)")
        self.ax.set_ylabel("Y (cm)")
        self.ax.set_zlabel("Z (cm)")

        # Calcula posiciones del robot
        T0 = SE3(0, 0, 0)
        T1 = T0 * SE3(self.robot_model.links[0].a * math.cos(q[0]),
                      self.robot_model.links[0].a * math.sin(q[0]), 0)
        T2 = T1 * SE3(self.robot_model.links[1].a * math.cos(q[0] + q[1]),
                      self.robot_model.links[1].a * math.sin(q[0] + q[1]), 0)

        # Coordenadas
        x = [0, T1.t[0], T2.t[0]]
        y = [0, T1.t[1], T2.t[1]]
        z = [0, 0, 0]

        # Dibuja el robot
        self.ax.plot(x, y, z, "-o", linewidth=4, markersize=8)
        self.ax.view_init(elev=30, azim=45)
        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
