import sys
import time
import threading
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from control import ServoController
from robot import SimuladorRobot

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("interface.ui", self)

        # Inicializa control físico y simulador
        self.control = ServoController()
        self.sim = SimuladorRobot()

        # Widgets
        self.sliders = [self.slider_q1, self.slider_q2, self.slider_q3, self.slider_q4]
        self.labels = [self.label_q1, self.label_q2, self.label_q3, self.label_q4]

        # Conectar sliders
        for i, slider in enumerate(self.sliders):
            slider.setMinimum(0)
            slider.setMaximum(180)
            slider.setValue(90)
            slider.valueChanged.connect(lambda val, idx=i: self.on_slider_move(idx, val))

        # Conectar botones
        self.btn_pick.clicked.connect(self.on_pick)
        self.btn_place.clicked.connect(self.on_place)

        # Loop de actualización
        threading.Thread(target=self.loop_sim, daemon=True).start()

    def on_slider_move(self, idx, val):
        """Cuando se mueve un slider"""
        self.labels[idx].setText(f"Joint {idx+1}: {val}°")
        self.control.set_angle(idx, val)

    def on_pick(self):
        self.control.pick()

    def on_place(self):
        self.control.place()

    def loop_sim(self):
        """Actualiza la simulación cada 0.1s"""
        while True:
            q = [s.value() for s in self.sliders]
            self.sim.actualizar(q)
            time.sleep(0.1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
