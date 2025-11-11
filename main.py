import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from roboticstoolbox import DHRobot, RevoluteDH
import numpy as np
from robot import Robot


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Brazo Robótico - Raspberry Pi 4")
        self.setGeometry(200, 100, 1000, 700)

        # --- Layout principal ---
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # --- Layout superior (sliders + botones) ---
        layout_superior = QHBoxLayout()
        layout_principal.addLayout(layout_superior)

        # --- Layout sliders ---
        layout_sliders = QVBoxLayout()
        layout_superior.addLayout(layout_sliders)

        self.robot = Robot()

        # Diccionario para almacenar sliders y etiquetas
        self.sliders = {}
        self.etiquetas = {}

        nombres = ["Base", "Hombro", "Codo", "Muñeca"]

        for i, nombre in enumerate(nombres, start=1):
            fila = QHBoxLayout()
            etiqueta = QLabel(f"{nombre}: 0°")
            etiqueta.setFixedWidth(120)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(180)
            slider.setValue(0)
            slider.valueChanged.connect(self.actualizar_robot)

            self.sliders[nombre.lower()] = slider
            self.etiquetas[nombre.lower()] = etiqueta

            fila.addWidget(etiqueta)
            fila.addWidget(slider)
            layout_sliders.addLayout(fila)

        # --- Botones para pinza ---
        layout_botones = QHBoxLayout()
        self.btn_abrir = QPushButton("Abrir Pinza")
        self.btn_cerrar = QPushButton("Cerrar Pinza")
        self.btn_abrir.clicked.connect(self.abrir_pinza)
        self.btn_cerrar.clicked.connect(self.cerrar_pinza)
        layout_botones.addWidget(self.btn_abrir)
        layout_botones.addWidget(self.btn_cerrar)
        layout_sliders.addLayout(layout_botones)

        # --- Simulación 3D ---
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        layout_principal.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111, projection='3d')

        # --- Modelo del robot en Peter Corke ---
        L1 = RevoluteDH(a=0, d=0.1, alpha=np.pi / 2)
        L2 = RevoluteDH(a=0.1, d=0, alpha=0)
        L3 = RevoluteDH(a=0.1, d=0, alpha=0)
        L4 = RevoluteDH(a=0.05, d=0, alpha=0)
        self.robot_model = DHRobot([L1, L2, L3, L4], name="Brazo_6DOF")

        # Estado inicial
        self.actualizar_robot()

    def actualizar_robot(self):
        # Leer los ángulos desde los sliders
        ang_base = self.sliders["base"].value()
        ang_hombro = self.sliders["hombro"].value()
        ang_codo = self.sliders["codo"].value()
        ang_muneca = self.sliders["muñeca"].value()

        # Actualizar etiquetas
        self.etiquetas["base"].setText(f"Base: {ang_base}°")
        self.etiquetas["hombro"].setText(f"Hombro: {ang_hombro}°")
        self.etiquetas["codo"].setText(f"Codo: {ang_codo}°")
        self.etiquetas["muñeca"].setText(f"Muñeca: {ang_muneca}°")

        # Mover servos físicos
        self.robot.mover_servo(0, ang_base)      # Base
        self.robot.mover_servo(1, ang_hombro)    # Hombro servo 1
        self.robot.mover_servo(2, ang_hombro)    # Hombro servo 2 (sincronizados)
        self.robot.mover_servo(3, ang_codo)      # Codo
        self.robot.mover_servo(4, ang_muneca)    # Muñeca

        # Actualizar simulación visual
        self.actualizar_simulacion(ang_base, ang_hombro, ang_codo, ang_muneca)

    def abrir_pinza(self):
        self.robot.mover_servo(5, 0)

    def cerrar_pinza(self):
        self.robot.mover_servo(5, 90)

    def actualizar_simulacion(self, base, hombro, codo, muneca):
        """Dibuja el modelo del robot manualmente en el canvas"""
        q_rad = np.radians([base, hombro, codo, muneca])
        T = self.robot_model.fkine_all(q_rad)

        # Extraer puntos de cada articulación
        xs = [0]
        ys = [0]
        zs = [0]
        for i in range(len(T)):
            xs.append(T[i].t[0])
            ys.append(T[i].t[1])
            zs.append(T[i].t[2])

        # Dibujar
        self.ax.clear()
        self.ax.plot(xs, ys, zs, '-o', linewidth=3, markersize=8)
        self.ax.set_xlim([-0.3, 0.3])
        self.ax.set_ylim([-0.3, 0.3])
        self.ax.set_zlim([0, 0.4])
        self.ax.set_title("Simulación 3D del Brazo Robótico")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
