import RPi.GPIO as GPIO
import time

class Ultrasonico:
    """
    Clase para manejar sensores ultrasónicos HC-SR04.
    """

    def __init__(self, trigger, echo):
        self.trigger = trigger
        self.echo = echo

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def medir(self):
        # Enviar pulso
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)

        t_inicio = time.time()
        t_fin = time.time()

        # Esperar inicio del eco
        while GPIO.input(self.echo) == 0:
            t_inicio = time.time()

        # Esperar fin del eco
        while GPIO.input(self.echo) == 1:
            t_fin = time.time()

        duracion = t_fin - t_inicio
        distancia = duracion * 17150  # velocidad sonido / 2

        return round(distancia, 1)
