import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from robot import Robot
from sensor import Ultrasonico  # Sensor de distancia


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot - Sin Simulaci�n")
        self.setGeometry(200, 100, 600, 400)

        # --- Inicializar clases principales ---
        self.robot = Robot()
        self.sensor = Ultrasonico()
        self.objeto_detectado = False  # Estado del sensor

        # --- Layout principal ---
        layout_principal = QVBoxLayout()

        # --- Sliders (4 articulaciones) ---
        self.sliders = []
        self.labels = []
        nombres = ["Base", "Hombro", "Codo", "Mu�eca"]

        for nombre in nombres:
            fila = QHBoxLayout()
            label = QLabel(f"{nombre}: 0�")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 180)
            slider.setValue(0)
            slider.valueChanged.connect(self.actualizar_robot)
            fila.addWidget(label)
            fila.addWidget(slider)
            layout_principal.addLayout(fila)
            self.labels.append(label)
            self.sliders.append(slider)

        # --- Botones de pinza ---
        botones = QHBoxLayout()
        btn_abrir = QPushButton("Abrir (Place)")
        btn_cerrar = QPushButton("Cerrar (Pick)")
        btn_abrir.clicked.connect(self.robot.place)
        btn_cerrar.clicked.connect(self.robot.pick)
        botones.addWidget(btn_abrir)
        botones.addWidget(btn_cerrar)
        layout_principal.addLayout(botones)

        # --- Estado ---
        self.status_label = QLabel("Distancia: -- cm | Estado: Normal")
        layout_principal.addWidget(self.status_label)

        # --- Widget principal ---
        widget = QWidget()
        widget.setLayout(layout_principal)
        self.setCentralWidget(widget)

        # --- Temporizador del sensor ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_distancia)
        self.timer.start(100)  # cada 100 ms

        self.actualizar_robot()

    def verificar_distancia(self):
        """Lee el sensor ultras�nico cada 100 ms"""
        try:
            dist = self.sensor.medir_distancia()
            self.status_label.setText(f"Distancia: {dist} cm")

            if dist < 10 and not self.objeto_detectado:
                self.objeto_detectado = True
                self.status_label.setText(f"Distancia: {dist} cm | ?? Objeto detectado � Robot detenido")
                QMessageBox.warning(self, "Alerta", "Objeto detectado a menos de 10 cm. Robot detenido.")
            elif dist >= 10 and self.objeto_detectado:
                self.objeto_detectado = False
                self.status_label.setText(f"Distancia: {dist} cm | ? Objeto despejado, robot activo.")
        except Exception as e:
            print("Error leyendo el sensor:", e)

    def actualizar_robot(self):
        """Actualiza los �ngulos de los servos f�sicos"""
        if self.objeto_detectado:
            # Si hay un objeto, no mover servos
            return

        angulos = [s.value() for s in self.sliders]
        nombres = ["Base", "Hombro", "Codo", "Mu�eca"]
        for i, label in enumerate(self.labels):
            label.setText(f"{nombres[i]}: {angulos[i]}�")

        base, hombro, codo, muneca = angulos
        self.robot.mover_servos(base, hombro)   # hombro mueve los 2 servos sincronizados
        self.robot.mover_codo(codo)
        self.robot.mover_muneca(muneca)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
