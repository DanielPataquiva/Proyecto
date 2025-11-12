from PyQt5 import QtWidgets, QtCore
from control import ServoController
from robot import SimuladorRobot
import sys

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control del Robot 4R")
        self.resize(600, 400)

        self.simulador = SimuladorRobot()
        self.servo_ctrl = ServoController()

        # Layout principal
        layout = QtWidgets.QVBoxLayout()

        # Sliders y etiquetas
        self.sliders = []
        self.labels = []

        nombres = ["Base", "Hombro", "Codo", "Muñeca"]

        for i, nombre in enumerate(nombres):
            box = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{nombre}: 90°")
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(180)
            slider.setValue(90)
            slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            slider.setTickInterval(10)

            # Cuando se mueve el slider, actualizar ángulo y GUI
            slider.valueChanged.connect(lambda value, idx=i: self.actualizar_angulo(idx, value))

            box.addWidget(label)
            box.addWidget(slider)

            layout.addLayout(box)
            self.labels.append(label)
            self.sliders.append(slider)

        # Botones de pinza
        botones = QtWidgets.QHBoxLayout()
        btn_pick = QtWidgets.QPushButton("Pick (Cerrar)")
        btn_place = QtWidgets.QPushButton("Place (Abrir)")
        btn_pick.clicked.connect(self.servo_ctrl.pick)
        btn_place.clicked.connect(self.servo_ctrl.place)
        botones.addWidget(btn_pick)
        botones.addWidget(btn_place)
        layout.addLayout(botones)

        self.setLayout(layout)

    def actualizar_angulo(self, idx, valor):
        """Actualiza la GUI, simulador y servo físico"""
        # 1️⃣ Actualiza la etiqueta del ángulo
        self.labels[idx].setText(f"{['Base', 'Hombro', 'Codo', 'Muñeca'][idx]}: {valor}°")

        # 2️⃣ Actualiza la simulación
        angulos = [s.value() for s in self.sliders]
        self.simulador.actualizar(angulos)

        # 3️⃣ Envía valor al servo correspondiente
        self.servo_ctrl.set_angle(idx, valor)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
