import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from roboticstoolbox import DHRobot, RevoluteDH

# -------------------------------
# CONFIGURACIÓN DEL ROBOT
# -------------------------------
class RobotSimulado(DHRobot):
    def __init__(self):
        L1 = RevoluteDH(d=0.1, a=0.1, alpha=np.pi / 2)
        L2 = RevoluteDH(d=0, a=0.1, alpha=0)
        L3 = RevoluteDH(d=0, a=0.1, alpha=0)
        L4 = RevoluteDH(d=0, a=0.1, alpha=0)
        L5 = RevoluteDH(d=0, a=0.05, alpha=0)
        L6 = RevoluteDH(d=0, a=0.05, alpha=0)
        super().__init__([L1, L2, L3, L4, L5, L6], name="Brazo 6DOF")

# Instancia del robot
robot = RobotSimulado()


# -------------------------------
# INTERFAZ GRÁFICA
# -------------------------------
class VentanaPrincipal(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación Brazo Robótico - Proyecto RPi")
        self.setGeometry(100, 100, 600, 500)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.angles = [90, 90, 90, 90, 90, 90]  # Inicial en 90°

        # Etiquetas para los servos
        self.labels = []
        self.sliders = []

        nombres_servos = [
            "Base (canal 0)",
            "Hombro (canales 1 y 2)",
            "Codo (canal 3)",
            "Muñeca (canal 4)",
            "Pinza (canal 5)",
        ]

        # Creamos sliders
        for i in range(6):
            hbox = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(f"Servo {i + 1}: {self.angles[i]}°")
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(180)
            slider.setValue(self.angles[i])
            slider.setTickInterval(10)
            slider.valueChanged.connect(self.crear_callback(i, label))

            hbox.addWidget(label)
            hbox.addWidget(slider)

            self.layout.addLayout(hbox)
            self.labels.append(label)
            self.sliders.append(slider)

        # Botón actualizar simulación
        self.boton_actualizar = QtWidgets.QPushButton("Actualizar simulación")
        self.boton_actualizar.clicked.connect(self.update_simulation)
        self.layout.addWidget(self.boton_actualizar)

        # Figura para la simulación
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.update_simulation()

    def crear_callback(self, index, label):
        def callback(value):
            self.angles[index] = value
            label.setText(f"Servo {index + 1}: {value}°")
            self.update_simulation()

        return callback

    def update_simulation(self):
        """Actualiza la simulación del robot sin cerrar la ventana."""
        q_rad = np.deg2rad(self.angles)

        try:
            self.ax.clear()
            robot.plot(q_rad, ax=self.ax, block=False, jointaxes=False, shadow=False)
            self.ax.set_title("Simulación 3D del Brazo Robótico")
            plt.pause(0.001)
        except Exception as e:
            print(f"⚠️ Error actualizando simulación: {e}")


# -------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
