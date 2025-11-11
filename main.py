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
        self.setWindowTitle("Control del Brazo Robótico - Simulación y Control Físico")
        self.setGeometry(200, 100, 1000, 600)

        # --- Robot físico ---
        self.robot = Robot()

        # --- Robot simulado (modelo 2 articulaciones por ahora) ---
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

        self.label1 = QtWidgets.QLabel("Articulación Base: 0°")
        self.slider1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider1.setRange(0, 180)
        self.slider1.setValue(0)

        self.label2 = QtWidgets.QLabel("Articulación Hombro: 0°")
        self.slider2 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider2.setRange(0, 180)
        self.slider2.setValue(0)

        # Botones de acción para la pinza (Pick & Place)
        self.btn_pick = QtWidgets.QPushButton("Pick (Cerrar Pinza)")
        self.btn_place = QtWidgets.QPushButton("Place (Abrir Pinza)")
        self.btn_reset = QtWidgets.QPushButton("Reset (0°)")

        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)

        controls_layout.addWidget(self.label1)
        controls_layout.addWidget(self.slider1)
        controls_layout.addWidget(self.label2)
        controls_layout.addWidget(self.slider2)
        controls_layout.addWidget(self.btn_pick)
        controls_layout.addWidget(self.btn_place)
        controls_layout.addWidget(self.btn_reset)
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

        # --- Conexión de sliders y botones ---
        self.slider1.valueChanged.connect(self.actualizar_robot)
        self.slider2.valueChanged.connect(self.actualizar_robot)
        self.btn_pick.clicked.connect(self.pick)
        self.btn_place.clicked.connect(self.place)
        self.btn_reset.clicked.connect(self.reset_robot)

        # --- Inicialización ---
        self.actualizar_robot()

    def actualizar_robot(self):
        """Actualiza los ángulos del robot físico y la simulación"""
        ang1 = self.slider1.value()
        ang2 = self.slider2.value()

        # Actualiza etiquetas
        self.label1.setText(f"Articulación Base: {ang1}°")
        self.label2.setText(f"Articulación Hombro: {ang2}°")

        # Mueve los servos reales (base + hombro doble)
        self.robot.mover_servos(ang1, ang2)

        # Muestra en la GUI los ángulos
        self.output_text.append(f"Base: {ang1}° | Hombro: {ang2}°")

        # Actualiza la simulación 3D
        self.dibujar_robot([math.radians(ang1), math.radians(ang2)])

    def dibujar_robot(self, q):
        """Dibuja el robot 2R en el espacio 3D según los ángulos"""
        self.ax.clear()
        self.ax.set_title("Simulación 3D - Brazo Robótico")
        self.ax.set_xlim(-20, 20)
        self.ax.set_ylim(-20, 20)
        self.ax.set_zlim(-1, 20)
        self.ax.set_xlabel("X (cm)")
        self.ax.set_ylabel("Y (cm)")
        self.ax.set_zlabel("Z (cm)")

        # Cinemática directa simple
        L1 = self.robot_model.links[0].a
        L2 = self.robot_model.links[1].a

        x0, y0, z0 = 0, 0, 0
        x1 = L1 * math.cos(q[0])
        y1 = L1 * math.sin(q[0])
        x2 = x1 + L2 * math.cos(q[0] + q[1])
        y2 = y1 + L2 * math.sin(q[0] + q[1])
        z1 = z2 = 0  # plano XY

        # Dibuja el robot
        self.ax.plot([x0, x1, x2], [y0, y1, y2], [z0, z1, z2], "-o", linewidth=4, markersize=8)
        self.ax.view_init(elev=30, azim=45)
        self.canvas.draw_idle()

    def pick(self):
        """Cierra la pinza"""
        self.robot.pick()
        self.output_text.append("Acción: PICK (Pinza cerrada)")

    def place(self):
        """Abre la pinza"""
        self.robot.place()
        self.output_text.append("Acción: PLACE (Pinza abierta)")

    def reset_robot(self):
        """Reinicia el robot a 0°"""
        self.slider1.setValue(0)
        self.slider2.setValue(0)
        self.robot.reset()
        self.output_text.append("Robot reiniciado a 0°")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
