# robot.py
from adafruit_servokit import ServoKit
import time

class Robot:
    def __init__(self, transition_delay=0.004):
        # Inicialización del controlador PCA9685
        self.kit = ServoKit(channels=16)
        self.transition_delay = transition_delay

        # Definición de los servos (los dos del hombro se controlan juntos)
        self.servos = {
            "base": [0],
            "hombro": [1, 2],  # Dos servos sincronizados
            "codo": [3],
            "muneca": [4],
            "pinza": [5]
        }

        # Configuración de rango de pulso
        for ch_list in self.servos.values():
            for ch in ch_list:
                try:
                    self.kit.servo[ch].set_pulse_width_range(500, 2500)
                    self.kit.servo[ch].actuation_range = 180
                except Exception as e:
                    print(f"⚠️ Advertencia al configurar canal {ch}: {e}")

        # Posiciones iniciales
        self.angles = {name: 90 for name in self.servos}
        self._aplicar_posiciones_iniciales()

    def _aplicar_posiciones_iniciales(self):
        for name, ch_list in self.servos.items():
            for ch in ch_list:
                try:
                    self.kit.servo[ch].angle = self.angles[name]
                except Exception as e:
                    print(f"⚠️ Error aplicando ángulo inicial en {name} (canal {ch}): {e}")
        print("✅ Servos inicializados en 90° (posición media).")

    def mover_servo(self, nombre, objetivo):
        """Mueve gradualmente un servo (o grupo de servos) al ángulo deseado."""
        if nombre not in self.servos:
            print(f"⚠️ Servo desconocido: {nombre}")
            return

        if not (0 <= objetivo <= 180):
            print(f"⚠️ Ángulo fuera de rango: {objetivo}")
            return

        actual = int(self.angles.get(nombre, 90))
        objetivo = int(objetivo)
        if objetivo == actual:
            return

        paso = 1 if objetivo > actual else -1

        try:
            for a in range(actual, objetivo, paso):
                for ch in self.servos[nombre]:
                    self.kit.servo[ch].angle = a
                time.sleep(self.transition_delay)
            # Posición final
            for ch in self.servos[nombre]:
                self.kit.servo[ch].angle = objetivo

            self.angles[nombre] = objetivo
            print(f"[{nombre}] movido a {objetivo}°")
        except Exception as e:
            print(f"⚠️ Error moviendo {nombre}: {e}")

    def set_servo_direct(self, nombre, angulo):
        """Mover sin interpolación."""
        if nombre not in self.servos:
            print(f"⚠️ Servo desconocido: {nombre}")
            return
        try:
            for ch in self.servos[nombre]:
                self.kit.servo[ch].angle = angulo
            self.angles[nombre] = angulo
            print(f"[{nombre}] set directo a {angulo}°")
        except Exception as e:
            print(f"⚠️ Error set directo {nombre}: {e}")

    def pick(self):
        """Pick: cerrar pinza (0°)."""
        print("🟢 PICK: cerrando pinza")
        self.mover_servo("pinza", 0)

    def place(self):
        """Place: abrir pinza (180°)."""
        print("🔵 PLACE: abriendo pinza")
        self.mover_servo("pinza", 180)
