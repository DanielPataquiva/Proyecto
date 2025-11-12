import time
import threading

try:
    # Intenta importar control físico (PCA9685)
    from adafruit_servokit import ServoKit
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

# Librerías para simulación 2D
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib.pyplot as plt
import numpy as np


class Robot:
    def __init__(self, use_physical=False):
        """
        Si use_physical=True → controla los servos reales (PCA9685)
        Si use_physical=False → simula el robot en 2D con Peter Corke
        """
        self.use_physical = use_physical and HARDWARE_AVAILABLE

        if self.use_physical:
            print("🦾 Modo FÍSICO activado")
            self.kit = ServoKit(channels=16)
            self.servo_base = 0
            self.servo_hombro_1 = 1
            self.servo_hombro_2 = 2
            self.servo_codo = 3
            self.servo_muneca = 4
            self.servo_pinza = 5
            self.reset()
        else:
            print("🧠 Modo SIMULACIÓN 2D activado")
            self._init_simulacion()

    # =====================================================
    # ---------- MODO FÍSICO ------------------------------
    # =====================================================
    def mover_servo(self, canal, angulo):
        try:
            self.kit.servo[canal].angle = angulo
            time.sleep(0.02)
        except Exception as e:
            print(f"Error servo {canal}: {e}")

    def mover_servos(self, ang_base, ang_hombro):
        if self.use_physical:
            self.mover_servo(self.servo_base, ang_base)
            self.mover_servo(self.servo_hombro_1, ang_hombro)
            self.mover_servo(self.servo_hombro_2, ang_hombro)
        else:
            self.q[0] = np.radians(ang_base)
            self.q[1] = np.radians(ang_hombro)
            self._update_plot()

    def mover_codo(self, angulo):
        if self.use_physical:
            self.mover_servo(self.servo_codo, angulo)
        else:
            self.q[2] = np.radians(angulo)
            self._update_plot()

    def mover_muneca(self, angulo):
        if self.use_physical:
            self.mover_servo(self.servo_muneca, angulo)
        else:
            self.q[3] = np.radians(angulo)
            self._update_plot()

    def pick(self):
        if self.use_physical:
            self.mover_servo(self.servo_pinza, 0)
        else:
            print("🤖 Pinza cerrando (Pick)")

    def place(self):
        if self.use_physical:
            self.mover_servo(self.servo_pinza, 180)
        else:
            print("🤖 Pinza abriendo (Place)")

    def reset(self):
        print("Inicializando posiciones del robot...")
        self.mover_servos(0, 0)
        self.mover_codo(0)
        self.mover_muneca(0)
        self.pick()

    # =====================================================
    # ---------- MODO SIMULACIÓN ---------------------------
    # =====================================================
    def _init_simulacion(self):
        # Define un brazo simple de 4 eslabones
        L1, L2, L3, L4 = 1, 0.8, 0.6, 0.4
        self.robot = DHRobot([
            RevoluteDH(a=L1, alpha=0),
            RevoluteDH(a=L2, alpha=0),
            RevoluteDH(a=L3, alpha=0),
            RevoluteDH(a=L4, alpha=0)
        ], name='BrazoSimulado')

        self.q = [0, 0, 0, 0]  # ángulos iniciales
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_aspect('equal')
        self.ax.set_title("Simulación 2D - Peter Corke")
        self.robot.plot(self.q, block=False, ax=self.ax)
        plt.ion()
        plt.show()

    def _update_plot(self):
        def update():
            self.ax.cla()
            self.ax.set_xlim(-3, 3)
            self.ax.set_ylim(-3, 3)
            self.ax.set_aspect('equal')
            self.ax.set_title("Simulación 2D - Peter Corke")
            self.robot.plot(self.q, block=False, ax=self.ax)
            plt.pause(0.001)

        threading.Thread(target=update, daemon=True).start()
