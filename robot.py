import time
from adafruit_servokit import ServoKit


class Robot:
    """
    Clase para controlar un brazo robótico con servomotores
    conectados a una placa PCA9685 (por ejemplo con la librería Adafruit ServoKit).
    """

    def __init__(self):
        # --- Inicialización del controlador de servos ---
        self.kit = ServoKit(channels=16)

        # --- Velocidad base de movimiento ---
        # Se puede modificar dinámicamente desde main.py
        self.velocidad = 0.05  # segundos entre movimientos

        # --- Canales asignados a cada articulación ---
        self.base_channel = 0
        self.hombro_channel = 1
        self.codo_channel = 2
        self.muneca_channel = 3
        self.pinza_channel = 4

        # --- Inicialización de posiciones ---
        self.pos_base = 90
        self.pos_hombro = 90
        self.pos_codo = 90
        self.pos_muneca = 90
        self.pos_pinza = 90

        self._inicializar_posiciones()

    # ---------------------------------------------------
    # Configuración inicial
    # ---------------------------------------------------
    def _inicializar_posiciones(self):
        """Mueve todos los servos a una posición inicial segura"""
        print("Inicializando posiciones del robot...")
        try:
            self.kit.servo[self.base_channel].angle = self.pos_base
            self.kit.servo[self.hombro_channel].angle = self.pos_hombro
            self.kit.servo[self.codo_channel].angle = self.pos_codo
            self.kit.servo[self.muneca_channel].angle = self.pos_muneca
            self.kit.servo[self.pinza_channel].angle = self.pos_pinza
            time.sleep(0.5)
            print("✅ Robot inicializado correctamente.")
        except Exception as e:
            print("⚠️ Error al inicializar posiciones:", e)

    # ---------------------------------------------------
    # Movimiento general
    # ---------------------------------------------------
    def mover_servos(self, base, hombro):
        """Mueve base y hombro simultáneamente"""
        try:
            self.mover_servo(self.base_channel, base)
            self.mover_servo(self.hombro_channel, hombro)
        except Exception as e:
            print("Error al mover servos base/hombro:", e)

    def mover_codo(self, codo):
        """Mueve el codo del robot"""
        self.mover_servo(self.codo_channel, codo)

    def mover_muneca(self, muneca):
        """Mueve la muñeca del robot"""
        self.mover_servo(self.muneca_channel, muneca)

    # ---------------------------------------------------
    # Pinza (apertura/cierre)
    # ---------------------------------------------------
    def pick(self):
        """Cierra la pinza (acción de agarre)"""
        print("🤖 Cerrando pinza (Pick)")
        self.mover_servo(self.pinza_channel, 30)  # valor típico de cerrado

    def place(self):
        """Abre la pinza (acción de soltar)"""
        print("🤖 Abriendo pinza (Place)")
        self.mover_servo(self.pinza_channel, 90)  # valor típico de abierto

    # ---------------------------------------------------
    # Función auxiliar
    # ---------------------------------------------------
    def mover_servo(self, canal, angulo):
        """
        Mueve un servo a un ángulo específico.
        Respeta la velocidad definida en self.velocidad.
        """
        try:
            angulo = max(0, min(180, angulo))  # limitar rango
            self.kit.servo[canal].angle = angulo
            time.sleep(self.velocidad)
        except Exception as e:
            print(f"⚠️ Error al mover el servo {canal}: {e}")

    # ---------------------------------------------------
    # Seguridad / apagado
    # ---------------------------------------------------
    def apagar_servos(self):
        """Apaga todos los servos (por seguridad o finalización)"""
        print("🛑 Apagando servos...")
        try:
            for i in range(5):
                self.kit.servo[i].angle = None
            print("✅ Servos apagados correctamente.")
        except Exception as e:
            print("⚠️ Error al apagar servos:", e)
