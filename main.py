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
        self.setWindowTitle("Control del Brazo Robótico - Simulación 2D (Raspberry Pi 4)")
        self.setGeometry(200, 100, 900, 600)

        # --- Layout principal ---
        layout_principal = QVBoxLayout()
        self.setLayout(layout_principal)

        # --- Layout superior (sliders y botones) ---
        layout_superior = QHBoxLayout()
        layout_principal.addLayout(layout_superior)

        # --- Layout sliders ---
        layout_sliders = QVBoxLayout()
        layout_superior.addLayout(layout_sliders)

        self.robot = Robot()

        # Diccionarios para sliders y etiquetas
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

        # --- Botones de pinza ---
        layout_botones = QHBoxLayout()
        self.btn_abrir = QPushButton("Abrir Pinza")
        self.btn_cerrar = QPushButton("Cerrar Pinza")
        self.btn_abrir.clicked.connect(self.abrir_pinza)
        self.btn_cerrar.clicked.connect(self.cerrar_pinza)
        layout_botones.addWidget(self.btn_abrir)
        layout_botones.addWidget(self.btn_cerrar)
        layout_sliders.addLayout(layout_botones)

        # --- Área de simulación (2D) ---
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        layout_principal.addWidget(self.canvas)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal', adjustable='datalim')

        # --- Modelo DH del robot (simplificado) ---
        L1 = RevoluteDH(a=0.1, d=0, alpha=0)
        L2 = RevoluteDH(a=0.1, d=0, alpha=0)
        L3 = RevoluteDH(a=0.08, d=0, alpha=0)
        L4 = RevoluteDH(a=0.06, d=0, alpha=0)
        self.robot_model = DHRobot([L1, L2, L3, L4], name="Brazo_2D")

        # Estado inicial
        self.actualizar_robot()

    def actualizar_robot(self):
        """Lee sliders, actualiza servos físicos y simulación."""
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

        # Actualizar simulación 2D
        self.actualizar_simulacion_2d(ang_base, ang_hombro, ang_codo, ang_muneca)

    def abrir_pinza(self):
        self.robot.mover_servo(5, 0)

    def cerrar_pinza(self):
        self.robot.mover_servo(5, 90)

    def actualizar_simulacion_2d(self, base, hombro, codo, muneca):
        """Dibuja la simulación 2D del brazo."""
        # Convertir a radianes
        q_rad = np.radians([base, hombro, codo, muneca])
        T = self.robot_model.fkine_all(q_rad)

        # Extraer puntos del plano XY
        xs = [0]
        ys = [0]
        for i in range(len(T)):
            xs.append(T[i].t[0])
            ys.append(T[i].t[2])  # usamos Z como Y en 2D

        # Dibujar brazo
        self.ax.clear()
        self.ax.plot(xs, ys, '-o', linewidth=3, markersize=6)
        self.ax.set_xlim([-0.3, 0.3])
        self.ax.set_ylim([0, 0.3])
        self.ax.set_title("Simulación 2D del Brazo Robótico")
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.grid(True)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
