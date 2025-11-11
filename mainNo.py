import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from robot import Robot
from sensor import Ultrasonico

# Forzar X11 en Raspberry Pi
os.environ["QT_QPA_PLATFORM"] = "xcb"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot - Sensor único")
        self.setGeometry(200, 100, 600, 400)

        # Robot y sensor
        self.robot = Robot()
        self.sensor = Ultrasonico()
        self.detener = False

        # Layout principal
        layout = QVBoxLayout()
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
            layout.addLayout(fila)
            self.labels.append(label)
            self.sliders.append(slider)

        # Botones pinza
        botones = QHBoxLayout()
        btn_pick = QPushButton("Pick")
        btn_place = QPushButton("Place")
        btn_pick.clicked.connect(self.robot.pick)
        btn_place.clicked.connect(self.robot.place)
        botones.addWidget(btn_pick)
        botones.addWidget(btn_place)
        layout.addLayout(botones)

        # Estado sensor
        self.estado_label = QLabel("Distancia: -- cm | Estado: Normal")
        layout.addWidget(self.estado_label)

        # Widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Timer sensor
        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_sensor)
        self.timer.start(100)  # cada 100 ms

        # Inicializar robot en cero
        self.actualizar_robot(initial=True)

    # Lectura sensor único
    def verificar_sensor(self):
        dist = self.sensor.medir_distancia_principal()
        estado = "Normal"
        if dist < 10:
            self.detener = True
            estado = "🚫 Detenido (objeto cercano)"
        else:
            self.detener = False

        self.estado_label.setText(f"Distancia: {dist:.1f} cm | Estado: {estado}")

    # Actualizar robot según sliders
    def actualizar_robot(self, initial=False):
        if self.detener and not initial:
            return

        angulos = [s.value() for s in self.sliders]
        for i, label in enumerate(self.labels):
            label.setText(f"{['Base','Hombro','Codo','Muñeca'][i]}: {angulos[i]}°")

        # Mover servos físicos
        self.robot.mover_servos(angulos[0], angulos[1])
        self.robot.mover_codo(angulos[2])
        self.robot.mover_muneca(angulos[3])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
