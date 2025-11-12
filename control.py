from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

class ServoController:
    def __init__(self):
        # Inicializar I2C
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c)
        self.pca.frequency = 50  # frecuencia estándar de servos

        # Asignar canales (puedes ajustar estos números según el cableado)
        self.servos = [0, 1, 2, 3]  # articulaciones
        self.gripper = 4            # pinza

    def angle_to_pwm(self, angle):
        """Convierte un ángulo (0–180°) a un valor PWM (duty 0–65535)"""
        pulse_min = 1000  # μs
        pulse_max = 2000  # μs
        pulse = pulse_min + (angle / 180.0) * (pulse_max - pulse_min)
        duty = int((pulse / 20000.0) * 65535)
        return duty

    def set_angle(self, servo_index, angle):
        """Mueve un servo de articulación"""
        channel = self.servos[servo_index]
        self.pca.channels[channel].duty_cycle = self.angle_to_pwm(angle)

    def pick(self):
        """Cierra pinza"""
        self.pca.channels[self.gripper].duty_cycle = self.angle_to_pwm(0)

    def place(self):
        """Abre pinza"""
        self.pca.channels[self.gripper].duty_cycle = self.angle_to_pwm(180)

    def stop(self):
        """Apaga servos"""
        for ch in self.servos + [self.gripper]:
            self.pca.channels[ch].duty_cycle = 0
        self.pca.deinit()
