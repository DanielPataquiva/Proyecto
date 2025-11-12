import sys
from PyQt5 import QtWidgets, uic
from control import ServoController
from robot import SimuladorRobot

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("interface.ui", self)

        self.servo_ctrl = ServoController()
        self.simulador = SimuladorRobot()

        # Conectar sliders
        self.slider_q1.valueChanged.connect(self.actualizar_robot)
        self.slider_q2.valueChanged.connect(self.actualizar_robot)
        self.slider_q3.valueChanged.connect(self.actualizar_robot)
        self.slider_q4.valueChanged.connect(self.actualizar_robot)

        # Botones Pick y Place
        self.btn_pick.clicked.connect(self.pick)
        self.btn_place.clicked.connect(self.place)

    def obtener_angulos(self):
        return [
            self.slider_q1.value(),
            self.slider_q2.value(),
            self.slider_q3.value(),
            self.slider_q4.value()
        ]

    def actualizar_robot(self):
        angulos = self.obtener_angulos()
        # Enviar a servos físicos
        for i, ang in enumerate(angulos):
            self.servo_ctrl.set_angle(i, ang)
        # Actualizar simulador
        self.simulador.actualizar(angulos)

    def pick(self):
        self.servo_ctrl.pick()

    def place(self):
        self.servo_ctrl.place()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
