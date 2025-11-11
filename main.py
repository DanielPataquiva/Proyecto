import sys
import math
import numpy as np
from PyQt5 import QtWidgets, QtCore
from robot import Robot
from roboticstoolbox import DHRobot, RevoluteDH
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot 2R - Simulación y Control Físico")

        # --- Instancia del robot físico ---
        self.robot = Robot()

        # --- Simulación 3D con Peter Corke ---
        L1 = 10
        L2 = 10
        self.robot_model = DHRobot([
            RevoluteDH(a=L1, alpha=0, d=0, offset=0),
            RevoluteDH(a=L2, alpha=0, d=0, offset=0)
        ], name='Robot 2R')

        # --- Configuración de interfaz ---
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Panel de controles ---
        control_layout = QtWidgets.QVBoxLayout()

        self.slider1 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider2 = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider1.setRange(0, 180)
        self.slider2.setRange(0, 180)

        self.slider1.setValue(0)
        self.slider2.setValue(0)

        self.label1 = QtWidgets.QLabel("Articulación 1: 0°")
        self.label2 = QtWidgets.QLabel("Articulación 2: 0°")

        control_layout.addWidget(self.label1)
        control_layout.addWidget(self.slider1)
        control_layout.addWidget(self.label2)
        control_layout.addWidget(self.slider2)

        # --- Botón para actualizar simulación ---
        self.btn_actualizar = QtWidgets.QPushButton("Actualizar Simulación")
        control_layout.addWidget(self.btn_actualizar)

        # --- Área de texto para mostrar ángulos ---
        self.text_output = QtWidgets.QTextEdit()
        self.text_output.setReadOnly(True)
        control_layout.addWidget(QtWidgets.QLabel("Lectura de ángulos:"))
        control_layout.addWidget(self.text_output)

        main_layout.addLayout(control_layout)

        # --- Simulación (canvas 3D) ---
        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        # --- Eventos ---
        self.slider1.valueChanged.connect(self.mover_robot)
        self.slider2.valueChanged.connect(self.mover_robot)
        self.btn_actualizar.clicked.connect(self.actualizar_simulacion)

        # --- Inicializar simulación ---
        self.actualizar_simulacion()

    def mover_robot(self):
        ang1 = self.slider1.value()
        ang2 = self.slider2.value()

        self.label1.setText(f"Articulación 1: {ang1}°")
        self.label2.setText(f"Articulación 2: {ang2}°")

        # Mueve los servos reales
        self.robot.mover_servos(ang1, ang2)

        # Actualiza texto en GUI
        self.text_output.append(f"Art1: {ang1}°, Art2: {ang2}°")

        # Actualiza la simulación 3D
        self.actualizar_simulacion()

    def actualizar_simulacion(self):
        ang1 = self.slider1.value()
        ang2 = self.slider2.value()
        q_rad = [math.radians(ang1), math.radians(ang2)]

        # Limpiar figura anterior
        self.fig.clear()

        # Crear nuevo subplot 3D
        ax = self.fig.add_subplot(111, projection='3d')
        ax.set_title("Simulación Robot 2R")

        # Dibujar robot en el entorno de Peter Corke
        self.robot_model.plot(q_rad, block=False)
        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
