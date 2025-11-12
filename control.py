from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import time

class ServoController:
    def __init__(self):
        # Inicializar I2C y PCA9685
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c)
        self.pca.frequency = 50  # Frecuencia típica de servos

        # Mapeo físico de los servos
        self.servo_base = 0       # Base rotacional
        self.servo_hombro_1 = 1   # Hombro izquierdo
        self.servo_hombro_2 = 2   # Hombro derecho (sincronizado)
        self.servo_codo = 3       # Codo
        self.servo_muneca = 4     # Muñeca
        self.servo_pinza = 5      # Pinza (pick/place)

    # Conversión de ángulo (°) a PWM (16 bits)
    def angle_to_pwm(self, angle):
        pulse_min = 1000  # µs
        pulse_max = 2000  # µs
        pulse = pulse_min + (angle / 180.0) * (pulse_max - pulse_min)
        duty = int((pulse / 20000.0) * 65535)
        return duty

    def set_angle(self, joint_index, angle):
        """Mueve un servo o grupo de servos según el índice del slider"""
        duty = self.angle_to_pwm(angle)

        if joint_index == 0:
            # Base rotacional
            self.pca.channels[self.servo_base].duty_cycle = duty

        elif joint_index == 1:
            # Hombro → mueve 2 servos sincronizados
            self.pca.channels[self.servo_hombro_1].duty_cycle = duty
            self.pca.channels[self.servo_hombro_2].duty_cycle = duty

        elif joint_index == 2:
            # Codo
            self.pca.channels[self.servo_codo].duty_cycle = duty

        elif joint_index == 3:
            # Muñeca
            self.pca.channels[self.servo_muneca].duty_cycle = duty

    def pick(self):
        """Cierra la pinza (servo 5)"""
        duty = self.angle_to_pwm(0)
        self.pca.channels[self.servo_pinza].duty_cycle = duty

    def place(self):
        """Abre la pinza (servo 5)"""
        duty = self.angle_to_pwm(180)
        self.pca.channels[self.servo_pinza].duty_cycle = duty

    def stop(self):
        """Apaga todos los servos"""
        for ch in range(6):
            self.pca.channels[ch].duty_cycle = 0
        self.pca.deinit()
