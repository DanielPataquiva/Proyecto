from adafruit_servokit import ServoKit
import time

class Robot:
    def __init__(self):
        # Inicializa la PCA9685 (16 canales)
        self.kit = ServoKit(channels=16)

        # Asignación de servos
        self.servo_base = 0
        self.servo_hombro_1 = 1
        self.servo_hombro_2 = 2
        self.servo_codo = 3
        self.servo_muneca = 4
        self.servo_pinza = 5

        # Inicializar en 0°
        self.reset()

    def mover_servo(self, canal, angulo):
        try:
            self.kit.servo[canal].angle = angulo
            time.sleep(0.02)  # pequeño delay
        except Exception as e:
            print(f"Error servo {canal}: {e}")

    def mover_servos(self, ang_base, ang_hombro):
        # Base
        self.mover_servo(self.servo_base, ang_base)
        # Hombros sincronizados
        self.mover_servo(self.servo_hombro_1, ang_hombro)
        self.mover_servo(self.servo_hombro_2, ang_hombro)

    def mover_codo(self, angulo):
        self.mover_servo(self.servo_codo, angulo)

    def mover_muneca(self, angulo):
        self.mover_servo(self.servo_muneca, angulo)

    def pick(self):
        self.mover_servo(self.servo_pinza, 0)

    def place(self):
        self.mover_servo(self.servo_pinza, 180)

    def reset(self):
        print("Inicializando posiciones del robot...")
        self.mover_servos(0, 0)
        self.mover_codo(0)
        self.mover_muneca(0)
        self.pick()
