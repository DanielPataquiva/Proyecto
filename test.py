import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from adafruit_servokit import ServoKit

# =====================================
# CONFIGURACIÓN PCA9685 Y CALIBRACIÓN
# =====================================

kit = ServoKit(channels=16)

# Configuración individual de servos
# min_angle / max_angle: limitan físicamente el movimiento
# offset: corrige el punto "cero" físico
# invert: invierte dirección si el servo está montado al revés
servo_config = {
    0: {"min_angle": 5, "max_angle": 175, "offset": -10, "invert": False},   # Articulación 1
    1: {"min_angle": 10, "max_angle": 170, "offset": 0,   "invert": False},   # Articulación 2 (servo A)
    2: {"min_angle": 10, "max_angle": 170, "offset": 0,   "invert": True},    # Articulación 2 (servo B)
    3: {"min_angle": 15, "max_angle": 165, "offset": 5,   "invert": False},   # Articulación 3
    4: {"min_angle": 5,  "max_angle": 175, "offset": 0,   "invert": False},   # Articulación 4
}

# Longitudes del brazo (para DH)
L1, L2, L3 = 5, 5, 5


# =====================================
# FUNCIONES DE CINEMÁTICA (DH)
# =====================================

def dh_matrix(theta, d, a, alpha):
    theta = np.deg2rad(theta)
    alpha = np.deg2rad(alpha)
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha), np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),               np.cos(alpha),               d],
        [0,              0,                           0,                           1]
    ])

def forward_kinematics(theta1, theta2, theta3, theta4):
    T1 = dh_matrix(theta1, 0, 0, 90)
    T2 = dh_matrix(theta2, 0, L1, 0)
    T3 = dh_matrix(theta3, 0, L2, 0)
    T4 = dh_matrix(theta4, 0, L3, 0)
    T = T1 @ T2 @ T3 @ T4
    pos = T[:3, 3]
    return pos


# =====================================
# INTERFAZ GRÁFICA
# =====================================

class ServoControl(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.labels = []
        self.sliders = []

        for i in range(4):  # 4 articulaciones (4 sliders)
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
        self.setWindowTitle("Control de 5 Servos (PCA9685 + Calibración + DH)")
        self.setGeometry(200, 200, 400, 300)

    def move_servo(self, index, angle):
        """Mueve los servos físicos y actualiza la cinemática"""

        if index == 0:
            self.set_servo_angle(0, angle)

        elif index == 1:
            # Articulación 2: dos servos sincronizados
            self.set_servo_angle(1, angle)
            self.set_servo_angle(2, angle)

        elif index == 2:
            self.set_servo_angle(3, angle)

        elif index == 3:
            self.set_servo_angle(4, angle)

        # Actualiza la etiqueta
        self.labels[index].setText(f"Articulación {index+1}: {angle}°")

        # Cinemática directa
        angles = [s.value() for s in self.sliders]
        pos = forward_kinematics(*angles)
        self.pos_label.setText(f"Posición final: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    def set_servo_angle(self, channel, angle):
        """Aplica calibración y mueve el servo"""
        cfg = servo_config[channel]
        min_a, max_a = cfg["min_angle"], cfg["max_angle"]
        offset, invert = cfg["offset"], cfg["invert"]

        # Aplica offset
        adj_angle = angle + offset

        # Limita dentro del rango permitido
        adj_angle = max(0, min(180, adj_angle))
        mapped_angle = np.interp(adj_angle, [0, 180], [min_a, max_a])

        # Inversión si está montado al revés
        if invert:
            mapped_angle = max_a - (mapped_angle - min_a)

        # Envía al servo
        kit.servo[channel].angle = mapped_angle


# =====================================
# PROGRAMA PRINCIPAL
# =====================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServoControl()
    window.show()
    sys.exit(app.exec_())
