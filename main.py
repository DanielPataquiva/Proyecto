import sys
import math
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from robot import Robot
from sensor import Ultrasonico  # 🧠 Importamos el sensor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control y Simulación del Robot 2D con Sensor")
        self.setGeometry(200, 100, 950, 700)

        self.robot = Robot()
        self.sensor = Ultrasonico()
        self.objeto_detectado = False  # 🔴 Se activa si hay algo a <10cm

        # --- Layout principal ---
        layout_principal = QVBoxLayout()

        # --- Sliders ---
        self.sliders = []
        self.labels = []
        nombres = ["Base", "Hombro", "Codo", "Muñeca"]
        for nombre in nombres:
            fila = QHBoxLayout()
            label = QLabel(f"{nombre}: 0°")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 180)
            slider.setValue(0)
            slider.valueChanged.connect(self.actualizar_robot)
            fila.addWidget(label)
            fila.addWidget(slider)
            layout_principal.addLayout(fila)
            self.labels.append(label)
            self.sliders.append(slider)

        # --- Botones ---
        botones = QHBoxLayout()
        btn_abrir = QPushButton("Abrir (Place)")
        btn_cerrar = QPushButton("Cerrar (Pick)")
        btn_abrir.clicked.connect(self.robot.place)
        btn_cerrar.clicked.connect(self.robot.pick)
        botones.addWidget(btn_abrir)
        botones.addWidget(btn_cerrar)
        layout_principal.addLayout(botones)

        # --- Simulación 2D ---
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout_principal.addWidget(self.canvas)

        # --- Barra de estado ---
        self.status_label = QLabel("Distancia: -- cm | Estado: Normal")
        layout_principal.addWidget(self.status_label)

        widget = QWidget()
        widget.setLayout(layout_principal)
        self.setCentralWidget(widget)

        # --- Timer para sensor (100 ms) ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_distancia)
        self.timer.start(100)

        self.actualizar_robot()

    def verificar_distancia(self):
        try:
            dist = self.sensor.medir_distancia()
            self.status_label.setText(f"Distancia: {dist} cm")

            if dist < 10 and not self.objeto_detectado:
                self.objeto_detectado = True
                self.status_label.setText(f"Distancia: {dist} cm | ⚠️ Objeto detectado — Robot detenido")
                QMessageBox.warning(self, "Alerta", "Objeto detectado a menos de 10 cm. Robot detenido.")
            elif dist >= 10 and self.objeto_detectado:
                self.objeto_detectado = False
                self.status_label.setText(f"Distancia: {dist} cm | ✅ Objeto despejado, robot activo.")
        except Exception as e:
            print("Error leyendo el sensor:", e)

    def actualizar_robot(self):
        if self.objeto_detectado:
            # 🚫 No mover mientras haya un objeto cerca
            return

        angulos = [s.value() for s in self.sliders]
        nombres = ["Base", "Hombro", "Codo", "Muñeca"]
        for i, label in enumerate(self.labels):
            label.setText(f"{nombres[i]}: {angulos[i]}°")

        base, hombro, codo, muneca = angulos
        self.robot.mover_servos(base, hombro)
        self.robot.mover_codo(codo)
        self.robot.mover_muneca(muneca)
        self.actualizar_simulacion(angulos)

    def actualizar_simulacion(self, angulos):
        L1, L2, L3, L4 = 0.1, 0.08, 0.06, 0.04
        rad = [math.radians(a) for a in angulos]

        x0, y0 = 0, 0
        x1 = L1 * math.cos(rad[0])
        y1 = L1 * math.sin(rad[0])
        x2 = x1 + L2 * math.cos(rad[0] + rad[1])
        y2 = y1 + L2 * math.sin(rad[0] + rad[1])
        x3 = x2 + L3 * math.cos(rad[0] + rad[1] + rad[2])
        y3 = y2 + L3 * math.sin(rad[0] + rad[1] + rad[2])
        x4 = x3 + L4 * math.cos(rad[0] + rad[1] + rad[2] + rad[3])
        y4 = y3 + L4 * math.sin(rad[0] + rad[1] + rad[2] + rad[3])

        self.ax.clear()
        self.ax.plot([x0, x1, x2, x3, x4], [y0, y1, y2, y3, y4],
                     '-o', linewidth=3, markersize=8, color='blue')
        self.ax.set_xlim(-0.3, 0.3)
        self.ax.set_ylim(-0.05, 0.3)
        self.ax.set_aspect('equal', 'box')
        self.ax.set_title("Simulación 2D del Robot (Vista XY)")
        self.ax.grid(True)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
