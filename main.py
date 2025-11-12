import sys
import threading
from PyQt5 import QtWidgets, uic, QtCore
from control import ServoController
from robot import SimuladorRobot


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("interface.ui", self)

        self.servo_ctrl = ServoController()
        self.simulador = SimuladorRobot()

        # --- Conectar sliders ---
        for slider in [self.slider_q1, self.slider_q2, self.slider_q3, self.slider_q4]:
            slider.valueChanged.connect(self.on_slider_change)
            slider.sliderReleased.connect(self.actualizar_robot)

        # --- Timer para control suave ---
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(200)  # 5 fps máximo
        self.update_timer.timeout.connect(self.actualizar_robot)
        self.update_timer_active = False

        # --- Botones ---
        self.btn_pick.clicked.connect(self.pick)
        self.btn_place.clicked.connect(self.place)

        # Últimos ángulos
        self.angulos_previos = [0, 0, 0, 0]

    def obtener_angulos(self):
        return [
            self.slider_q1.value(),
            self.slider_q2.value(),
            self.slider_q3.value(),
            self.slider_q4.value()
        ]

    def on_slider_change(self):
        """Evita saturar CPU mientras se arrastra el slider"""
        if not self.update_timer_active:
            self.update_timer.start()
            self.update_timer_active = True

    def actualizar_robot(self):
        """Actualiza servos y simulador sin sobrecargar CPU"""
        angulos = self.obtener_angulos()

        # Evita actualizaciones redundantes
        if angulos == self.angulos_previos:
            return
        self.angulos_previos = angulos

        # Actualiza los servos en un hilo (para no congelar GUI)
        threading.Thread(target=self.mover_servos, args=(angulos,), daemon=True).start()

        # Actualiza la simulación (menos frecuente)
        self.simulador.actualizar(angulos)

        # Detiene el timer si no hay más movimiento
        self.update_timer.stop()
        self.update_timer_active = False

    def mover_servos(self, angulos):
        """Controla servos sin bloquear interfaz"""
        try:
            for i, ang in enumerate(angulos):
                self.servo_ctrl.set_angle(i, ang)
        except Exception as e:
            print(f"⚠️ Error moviendo servos: {e}")

    def pick(self):
        threading.Thread(target=self.servo_ctrl.pick, daemon=True).start()

    def place(self):
        threading.Thread(target=self.servo_ctrl.place, daemon=True).start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
