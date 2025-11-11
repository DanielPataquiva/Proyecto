from adafruit_servokit import ServoKit
import time

class Robot:
    def __init__(self):
        # Inicializa la PCA9685 (controladora de servos)
        self.kit = ServoKit(channels=16)

        # Asignación de canales para los 6 servos del brazo
        self.servo_base = 0          # Base giratoria
        self.servo_hombro_1 = 1      # Hombro izquierdo
        self.servo_hombro_2 = 2      # Hombro derecho (sincronizado)
        self.servo_codo = 3          # Codo
        self.servo_muneca = 4        # Muñeca
        self.servo_pinza = 5         # Pinza (actuador final)

        # Posición inicial
        self.reset()

    def mover_servo(self, canal, angulo):
        """Mueve un solo servo al ángulo especificado (0–180°)."""
        try:
            self.kit.servo[canal].angle = angulo
        except Exception as e:
            print(f"Error al mover el servo {canal}: {e}")

    def mover_servos(self, ang_base, ang_hombro):
        """Mueve los servos de la base y ambos hombros al tiempo."""
        try:
            # Base giratoria
            self.kit.servo[self.servo_base].angle = ang_base
            # Hombros sincronizados
            self.kit.servo[self.servo_hombro_1].angle = ang_hombro
            self.kit.servo[self.servo_hombro_2].angle = ang_hombro
        except Exception as e:
            print(f"Error al mover servos base/hombro: {e}")

    def mover_codo(self, angulo):
        """Mueve el codo."""
        self.mover_servo(self.servo_codo, angulo)

    def mover_muneca(self, angulo):
        """Mueve la muñeca."""
        self.mover_servo(self.servo_muneca, angulo)

    def pick(self):
        """Cierra la pinza."""
        self.mover_servo(self.servo_pinza, 0)

    def place(self):
        """Abre la pinza."""
        self.mover_servo(self.servo_pinza, 180)

    def reset(self):
        """Lleva todos los servos a 0°."""
        print("Reiniciando robot a posición inicial...")
        self.kit.servo[self.servo_base].angle = 0
        self.kit.servo[self.servo_hombro_1].angle = 0
        self.kit.servo[self.servo_hombro_2].angle = 0
        self.kit.servo[self.servo_codo].angle = 0
        self.kit.servo[self.servo_muneca].angle = 0
        self.kit.servo[self.servo_pinza].angle = 0
        time.sleep(0.1)
