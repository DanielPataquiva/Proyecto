import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from adafruit_servokit import ServoKit

# ========================
# CONFIGURACIÓN DE SERVOS
# ========================
kit = ServoKit(channels=16)

# Ajustes de servo: canal, rango, inversión, etc.
# Si tu servo está invertido, pon "invert=True"
servo_config = {
    0: {"min_angle": 0,   "max_angle": 180, "invert": False},  # Articulación 1
    1: {"min_angle": 10,  "max_angle": 170, "invert": False},  # Articulación 2 (servo 1)
    2: {"min_angle": 10,  "max_angle": 170, "invert": True},   # Articulación 2 (servo 2, invertido)
    3: {"min_angle": 20,  "max_angle": 160, "invert": False},  # Articulación 3
    4: {"min_angle": 0,   "max_angle": 180, "invert": False},  # Articulación 4
}

# Longitudes de los eslabones (ajusta según tu brazo)
L1, L2, L3 = 9, 9, 9


# ========================
# FUNCIONES DE CINEMÁTICA
# ========================

def dh_matrix(theta, d, a, alpha):
    """Matriz DH estándar"""
    theta = np.deg2rad(theta)
    alpha = np.deg2rad(alpha)
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),               np.cos(alpha),               d],
        [0,              0,                           0,                           1]
    ])


def forward_kinematics(theta1, theta2, theta3, theta4):
    """Cinemática directa usando parámetros DH"""
    T1 = dh_matrix(theta1, 0, 0, 90)
    T2 = dh_matrix(theta2, 0, L1, 0)
    T3 = dh_matrix(theta3, 0, L2, 0)
    T4 = dh_matrix(theta4, 0, L3, 0)
    T = T1 @ T2 @ T3 @ T4
    pos = T[:3, 3]
    return pos


# ========================
# CLASE DE INTERFAZ GRÁFICA
# ========================

class ServoControl(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.labels = []
        self.sliders = []

        for i in range(4):  # Solo 4 sliders (4 articulaciones)
            lbl = QLabel(f"Articulación {i+1}: 90°", self)
            sld = QSlider(Qt.Horizontal, self)
            sld.setMinimum(0)
            sld.setMaximum(180)
            sld.setValue(90)
            sld.valueChanged.connect(lambda val, idx=i: self.move_servo(idx, val))
            layout.addWidget(lbl)
            layout.addWidget(sld)
            self.labels.append(lbl)
            self.sliders.append(sld)

        self.pos_label = QLabel("Posición final: (x, y, z)", self)
        layout.addWidget(self.pos_label)

        self.setLayout(layout)
        self.setWindowTitle("Control de 5 Servos (PCA9685 + DH)")
        self.setGeometry(200, 200, 400, 300)

    def move_servo(self, index, angle):
        """Mueve los servos físicos con sus rangos e inversiones"""

        if index == 0:
            self.set_servo_angle(0, angle)

        elif index == 1:
            # Articulación 2 tiene 2 servos sincronizados
            self.set_servo_angle(1, angle)
            self.set_servo_angle(2, angle)

        elif index == 2:
            self.set_servo_angle(3, angle)

        elif index == 3:
            self.set_servo_angle(4, angle)

        # Actualiza texto del slider
        self.labels[index].setText(f"Articulación {index+1}: {angle}°")

        # Calcula posición DH
        angles = [s.value() for s in self.sliders]
        pos = forward_kinematics(*angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    def set_servo_angle(self, channel, angle):
        """Ajusta ángulo considerando rango e inversión"""
        cfg = servo_config[channel]
        min_a, max_a = cfg["min_angle"], cfg["max_angle"]
        invert = cfg["invert"]

        # Escalado y corrección por inversión
        mapped_angle = np.interp(angle, [0, 180], [min_a, max_a])
        if invert:
            mapped_angle = max_a - (mapped_angle - min_a)

        kit.servo[channel].angle = mapped_angle


# ========================
# PROGRAMA PRINCIPAL
# ========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
