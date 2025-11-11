import RPi.GPIO as GPIO
import time

class Ultrasonico:
    def __init__(self, trig=23, echo=24):
        self.trig = trig
        self.echo = echo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trig, False)
        time.sleep(0.1)

    def medir_distancia(self):
        """Devuelve la distancia en centímetros"""
        GPIO.output(self.trig, True)
        time.sleep(0.00001)
        GPIO.output(self.trig, False)

        # Esperar el pulso de respuesta
        start = time.time()
        stop = time.time()

        while GPIO.input(self.echo) == 0:
            start = time.time()

        while GPIO.input(self.echo) == 1:
            stop = time.time()

        tiempo = stop - start
        distancia = (tiempo * 34300) / 2  # en cm
        return round(distancia, 1)

    def limpiar(self):
        GPIO.cleanup()
