import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from robot import Robot
from sensor import Ultrasonico

# ------------------------------
# Forzar X11 en Raspberry Pi
# ------------------------------
os.environ["QT_QPA_PLATFORM"] = "xcb"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot - Doble Sensor")
        self.setGeometry(200, 100, 600, 400)

        # Robot y sensores
        self.robot = Robot()
        self.sensores = Ultrasonico()
        self.detener = False
        self.modo_lento = False

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

        # Estado sensores
        self.estado_label = QLabel("Distancias: -- cm | Estado: Normal")
        layout.addWidget(self.estado_label)

        # Widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Timer sensores
        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_sensores)
        self.timer.start(100)  # cada 100 ms

        # Inicializar robot en cero sin retraso extra
        self.actualizar_robot(initial=True)

    # ---------------------------------
    # Lectura sensores
    # ---------------------------------
    def verificar_sensores(self):
        dist1 = self.sensores.medir_distancia_principal()
        dist2 = self.sensores.medir_distancia_secundario()
        estado = "Normal"

        # Sensor principal: detener < 10cm
        if dist1 < 10:
            self.detener = True
            estado = "🚫 Detenido (objeto cercano)"
        else:
            self.detener = False

        # Sensor secundario: lento < 5cm
        if dist2 < 5:
            self.modo_lento = True
            if estado == "Normal":
                estado = "🐢 Modo lento"
        else:
            self.modo_lento = False

        self.estado_label.setText(
            f"Distancia1: {dist1:.1f} cm | Distancia2: {dist2:.1f} cm | Estado: {estado}"
        )

    # ---------------------------------
    # Actualizar robot según sliders
    # ---------------------------------
    def actualizar_robot(self, initial=False):
        if self.detener and not initial:
            return

        angulos = [s.value() for s in self.sliders]
        for i, label in enumerate(self.labels):
            label.setText(f"{['Base','Hombro','Codo','Muñeca'][i]}: {angulos[i]}°")

        # Ajustar velocidad
        self.robot.velocidad = 0.15 if self.modo_lento else 0.05

        # Mover servos físicos
        self.robot.mover_servos(angulos[0], angulos[1])
        self.robot.mover_codo(angulos[2])
        self.robot.mover_muneca(angulos[3])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
