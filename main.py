# main.py
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from robot import Robot

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("interface.ui", self)

        # Instancia el robot (usa hardware si está disponible)
        self.robot = Robot(use_physical=True)

        # Valores iniciales
        self.slider_base.setValue(90)
        self.slider_hombro.setValue(90)
        self.slider_codo.setValue(90)
        self.slider_muneca.setValue(90)
        self.slider_pinza.setValue(90)

        # Embedir Matplotlib en sim_frame
        self.fig = Figure(figsize=(5.2, 4.8))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Limpiar el layout del frame y añadir canvas
        layout = QtWidgets.QVBoxLayout(self.sim_frame)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.canvas)

        # Inicializar simulación en robot
        self.robot.init_simulation_canvas(self.fig, self.ax)
        self.robot.update_simulation()

        # Conectar sliders
        self.slider_base.valueChanged.connect(self.on_base)
        self.slider_hombro.valueChanged.connect(self.on_hombro)
        self.slider_codo.valueChanged.connect(self.on_codo)
        self.slider_muneca.valueChanged.connect(self.on_muneca)
        self.slider_pinza.valueChanged.connect(self.on_pinza)

        # Botones
        self.btn_pick.clicked.connect(self.on_pick)
        self.btn_place.clicked.connect(self.on_place)

        # Mostrar valores iniciales
        self._update_angle_labels()

        self.show()

    # ---- callback sliders ----
    def on_base(self, v):
        self.robot.mover_servo("base", v)
        self._update_angle_labels()

    def on_hombro(self, v):
        self.robot.mover_servo("hombro", v)
        self._update_angle_labels()

    def on_codo(self, v):
        self.robot.mover_servo("codo", v)
        self._update_angle_labels()

    def on_muneca(self, v):
        self.robot.mover_servo("muneca", v)
        self._update_angle_labels()

    def on_pinza(self, v):
        # mover manual de pinza
        self.robot.set_servo_direct("pinza", v)
        self._update_angle_labels()

    # ---- botones pick/place ----
    def on_pick(self):
        self.robot.pick()
        # actualizar slider_pinza y labels
        self.slider_pinza.setValue(self.robot.angles["pinza"])
        self._update_angle_labels()

    def on_place(self):
        self.robot.place()
        self.slider_pinza.setValue(self.robot.angles["pinza"])
        self._update_angle_labels()

    # ---- UI labels ----
    def _update_angle_labels(self):
        self.label_ang_base.setText(f"{self.robot.angles['base']}°")
        self.label_ang_hombro.setText(f"{self.robot.angles['hombro']}°")
        self.label_ang_codo.setText(f"{self.robot.angles['codo']}°")
        self.label_ang_muneca.setText(f"{self.robot.angles['muneca']}°")
        self.label_ang_pinza.setText(f"{self.robot.angles['pinza']}°")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())