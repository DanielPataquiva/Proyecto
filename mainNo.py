import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from robot import Robot
from sensor import Ultrasonico

os.environ["QT_QPA_PLATFORM"] = "xcb"


class SensorThread(QThread):
    distancia_signal = pyqtSignal(float, float)  

    def __init__(self, sensor):
        super().__init__()
        self.sensor = sensor
        self.running = True

    def run(self):
        while self.running:
            d1 = self.sensor.medir_distancia_principal()
            d2 = self.sensor.medir_distancia_secundario()
            self.distancia_signal.emit(d1, d2)
            self.msleep(100)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modo Manual")
        self.setGeometry(200, 100, 600, 400)

        
        self.robot = Robot()
        self.sensor = Ultrasonico()
        self.detener = False
        self.ralentizar = False

       
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
        self.estado_label = QLabel("Distancia principal: -- cm | secundario: -- cm | Estado: Normal")
        layout.addWidget(self.estado_label)

        # Widget central
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Hilo de sensores
        self.sensor_thread = SensorThread(self.sensor)
        self.sensor_thread.distancia_signal.connect(self.actualizar_estado_sensores)
        self.sensor_thread.start()

        # Inicializar robot
        self.actualizar_robot(initial=True)


    def actualizar_estado_sensores(self, d1, d2):
        estado = "Normal"
        self.detener = False
        self.ralentizar = False

        if d1 < 10:
            self.detener = True
            estado = "🚫 Detenido (sensor principal)"
        elif d2 < 5:
            self.ralentizar = True
            estado = "⚠️ Movimiento lento (sensor secundario)"

        self.estado_label.setText(
            f"Distancia principal: {d1:.1f} cm | secundario: {d2:.1f} cm | Estado: {estado}"
        )

    # ==============================
    # Mover robot
    # ==============================
    def actualizar_robot(self, initial=False):
        if self.detener and not initial:
            return

        angulos = [s.value() for s in self.sliders]
        if self.ralentizar:

            angulos = [a // 2 for a in angulos]

        for i, label in enumerate(self.labels):
            label.setText(f"{['Base','Hombro','Codo','Muñeca'][i]}: {angulos[i]}°")

        self.robot.mover_servos(angulos[0], angulos[1])
        self.robot.mover_codo(angulos[2])
        self.robot.mover_muneca(angulos[3])

    # ==============================
    # Al cerrar ventana
    # ==============================
    def closeEvent(self, event):
        self.sensor_thread.stop()
        self.sensor.cleanup()
        event.accept()

# ==============================
# Programa principal

# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
