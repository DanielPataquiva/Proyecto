import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from robot import Robot



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot - Doble Sensor")
        self.setGeometry(200, 100, 600, 400)

        # --- Inicialización de componentes ---
        self.robot = Robot()
        #self.sensor_principal = Ultrasonico(trigger_pin=23, echo_pin=24)  # Ejemplo pines
        #self.sensor_secundario = Ultrasonico(trigger_pin=17, echo_pin=27)  # Ejemplo pines
        self.objeto_detectado = False
        self.modo_lento = False

        # --- Layout principal ---
        layout_principal = QVBoxLayout()

        # --- Sliders (4 articulaciones) ---
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
        self.status_label = QLabel("Distancia 1: -- cm | Distancia 2: -- cm | Estado: Normal")
        layout_principal.addWidget(self.status_label)

        # --- Widget principal ---
        widget = QWidget()
        widget.setLayout(layout_principal)
        self.setCentralWidget(widget)

        # --- Timer del sensor ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_sensores)
        self.timer.start(100)  # cada 100 ms

        self.actualizar_robot()

    def verificar_sensores(self):
        """Verifica ambos sensores y ajusta el comportamiento del robot."""
        try:
            dist1 = self.sensor_principal.medir_distancia()
            dist2 = self.sensor_secundario.medir_distancia()

            texto_estado = f"Distancia 1: {dist1:.1f} cm | Distancia 2: {dist2:.1f} cm"

            # --- Sensor principal (<10cm) -> detener robot ---
            if dist1 < 10 and not self.objeto_detectado:
                self.objeto_detectado = True
                texto_estado += " | ⚠️ Objeto cercano (robot detenido)"
                QMessageBox.warning(self, "Alerta", "Objeto detectado a menos de 10 cm. Robot detenido.")
            elif dist1 >= 10 and self.objeto_detectado:
                self.objeto_detectado = False
                texto_estado += " | ✅ Objeto despejado"

            # --- Sensor secundario (<5cm) -> modo lento ---
            if dist2 < 5 and not self.modo_lento:
                self.modo_lento = True
                texto_estado += " | 🕐 Modo lento activado"
            elif dist2 >= 5 and self.modo_lento:
                self.modo_lento = False
                texto_estado += " | ⚡ Modo normal"

            self.status_label.setText(texto_estado)

        except Exception as e:
            print("Error al leer sensores:", e)

    def actualizar_robot(self):
        """Actualiza el movimiento físico del robot"""
        if self.objeto_detectado:
            # Si el sensor principal detecta algo, no mover servos
            return

        angulos = [s.value() for s in self.sliders]
        nombres = ["Base", "Hombro", "Codo", "Muñeca"]

        for i, label in enumerate(self.labels):
            label.setText(f"{nombres[i]}: {angulos[i]}°")

        base, hombro, codo, muneca = angulos

        # --- Ajustar velocidad según el modo ---
        if self.modo_lento:
            self.robot.velocidad = 0.15  # más lento
        else:
            self.robot.velocidad = 0.05  # normal

        self.robot.mover_servos(base, hombro)
        self.robot.mover_codo(codo)
        self.robot.mover_muneca(muneca)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
