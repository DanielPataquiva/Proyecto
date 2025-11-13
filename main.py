import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer
from simulacion import Simulacion
import control
from interfaz_ui import Ui_Form  # generado por pyuic5

class MainApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.angles = [0, 0, 0, 0]  # Posición inicial en 0
        self.sim = Simulacion()

        # Conectar sliders
        self.slider1.valueChanged.connect(lambda val: self.slider_changed(0, val))
        self.slider2.valueChanged.connect(lambda val: self.slider_changed(1, val))
        self.slider3.valueChanged.connect(lambda val: self.slider_changed(2, val))
        self.slider4.valueChanged.connect(lambda val: self.slider_changed(3, val))

        # Conectar botones Pick/Place
        self.btnPick.clicked.connect(control.pick)
        self.btnPlace.clicked.connect(control.place)

        # Actualizar simulación periódicamente
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.sim.update(self.angles))
        self.timer.start(100)

    def slider_changed(self, index, val):
        self.angles[index] = val
        control.move_joint(index, val)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
