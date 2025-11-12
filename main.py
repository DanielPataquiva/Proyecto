import sys
import numpy as np
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3
from robot import Robot  # Control físico de los servos

# Clase principal de la interfaz
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("interface.ui", self)

        # Crear figura 3D en el widget
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvas(self.fig)
        self.layout_sim.addWidget(self.canvas)

        # Crear el robot físico
        self.robot_fisico = Robot()

        # Crear el modelo cinemático (Peter Corke)
        self.robot_model = DHRobot(
            [
                RevoluteDH(a=0.05, alpha=np.pi / 2, d=0),
                RevoluteDH(a=0.15, alpha=0, d=0),
                RevoluteDH(a=0.15, alpha=0, d=0),
                RevoluteDH(a=0.10, alpha=0, d=0),
                RevoluteDH(a=0.10, alpha=0, d=0),
                RevoluteDH(a=0.05, alpha=0, d=0),
            ],
            name="Brazo_Robotico"
        )

        # Inicializar todos los ángulos en 0°
        self.angles = [0, 0, 0, 0, 0, 0]

        # Configurar sliders para cada articulación
        self.slider_base.setMinimum(0)
        self.slider_base.setMaximum(180)
        self.slider_base.setValue(0)

        self.slider_hombro.setMinimum(0)
        self.slider_hombro.setMaximum(180)
        self.slider_hombro.setValue(0)

        self.slider_codo.setMinimum(0)
        self.slider_codo.setMaximum(180)
        self.slider_codo.setValue(0)

        self.slider_muneca.setMinimum(0)
        self.slider_muneca.setMaximum(180)
        self.slider_muneca.setValue(0)

        # El control del actuador (pinza)
        self.slider_pinza.setMinimum(0)
        self.slider_pinza.setMaximum(180)
        self.slider_pinza.setValue(0)

        # Conexión de sliders
        self.slider_base.valueChanged.connect(lambda v: self.actualizar_servo(0, v))
        self.slider_hombro.valueChanged.connect(lambda v: self.actualizar_servo(1, v))
        self.slider_codo.valueChanged.connect(lambda v: self.actualizar_servo(2, v))
        self.slider_muneca.valueChanged.connect(lambda v: self.actualizar_servo(3, v))
        self.slider_pinza.valueChanged.connect(lambda v: self.actualizar_servo(4, v))

        # Conexión de botones Pick y Place
        self.btn_pick.clicked.connect(self.pick)
        self.btn_place.clicked.connect(self.place)

        # Mostrar la posición inicial del robot
        self.actualizar_simulacion()
        self.mostrar_angulos()

    # Función que actualiza servos y simulación
    def actualizar_servo(self, indice, valor):
        # Actualizar ángulo interno
        self.angles[indice] = valor
        print(f"Servo {indice+1}: {valor}°")

        # Actualizar robot físico
        self.robot_fisico.mover_servo(indice, valor)

        # Actualizar simulación 3D
        self.actualizar_simulacion()
        self.mostrar_angulos()

    # Botón Pick (cerrar pinza)
    def pick(self):
        self.angles[5] = 0  # Servo 6 (pinza)
        self.robot_fisico.pick()
        self.actualizar_simulacion()
        self.mostrar_angulos()

    # Botón Place (abrir pinza)
    def place(self):
        self.angles[5] = 180  # Servo 6 (pinza)
        self.robot_fisico.place()
        self.actualizar_simulacion()
        self.mostrar_angulos()

    # Actualizar simulación 3D con los ángulos actuales
    def actualizar_simulacion(self):
        q_rad = [np.deg2rad(a) for a in self.angles]
        self.ax.cla()  # Limpiar figura
        self.robot_model.plot(q_rad, block=False, ax=self.ax)
        self.ax.set_xlim(-0.5, 0.5)
        self.ax.set_ylim(-0.5, 0.5)
        self.ax.set_zlim(0, 0.5)
        self.ax.set_title("Simulación Brazo Robótico (0° Inicial)")
        self.canvas.draw()

    # Mostrar ángulos en cuadro de texto
    def mostrar_angulos(self):
        texto = "\n".join(
            [f"Servo {i+1}: {a}°" for i, a in enumerate(self.angles)]
        )
        self.txt_angulos.setPlainText(texto)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())