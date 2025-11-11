import RPi.GPIO as GPIO
import time

class Ultrasonico:
    """
    Clase para manejar dos sensores HC-SR04.
    """

    def __init__(self, trigger_principal=23, echo_principal=24,
                 trigger_secundario=17, echo_secundario=27):
        # Pines del sensor principal
        self.trig1 = trigger_principal
        self.echo1 = echo_principal

        # Pines del sensor secundario
        self.trig2 = trigger_secundario
        self.echo2 = echo_secundario

        # Configuración de pines
        GPIO.setmode(GPIO.BCM)
        for pin in [self.trig1, self.trig2]:
            GPIO.setup(pin, GPIO.OUT)
        for pin in [self.echo1, self.echo2]:
            GPIO.setup(pin, GPIO.IN)

    def medir_distancia_principal(self):
        return self._medir_distancia(self.trig1, self.echo1)

    def medir_distancia_secundario(self):
        return self._medir_distancia(self.trig2, self.echo2)

    def _medir_distancia(self, trig, echo):
        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        start = time.time()
        stop = time.time()

        # Esperar a que suba el ECHO
        while GPIO.input(echo) == 0:
            start = time.time()
        # Esperar a que baje el ECHO
        while GPIO.input(echo) == 1:
            stop = time.time()

        tiempo_transcurrido = stop - start
        distancia_cm = (tiempo_transcurrido * 34300) / 2
        return distancia_cm

    def cleanup(self):
        GPIO.cleanup()
