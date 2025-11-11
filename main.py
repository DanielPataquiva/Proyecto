# main.py
import sys
from PyQt5 import QtWidgets, uic
from robot import Robot

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Carga la interfaz
        uic.loadUi("interface.ui", self)

        # Inicializa el controlador del robot
        self.robot = Robot()

        # Conexión de sliders → servos
        self.slider_base.valueChanged.connect(lambda v: self._on_slider("base", v))
        self.slider_hombro.valueChanged.connect(lambda v: self._on_slider("hombro", v))
        self.slider_codo.valueChanged.connect(lambda v: self._on_slider("codo", v))
        self.slider_muneca.valueChanged.connect(lambda v: self._on_slider("muneca", v))
        self.slider_pinza.valueChanged.connect(lambda v: self._on_slider("pinza", v))

        # Botones Pick y Place
        self.btn_pick.clicked.connect(self.robot.pick)
        self.btn_place.clicked.connect(self.robot.place)

        # Muestra la interfaz
        self.show()

    def _on_slider(self, nombre, valor):
        """Callback cuando se mueve un slider"""
        self.robot.mover_servo(nombre, valor)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
