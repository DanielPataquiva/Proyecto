import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton,
    QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# ======================================
# CLASE ROBOT FÍSICO
# ======================================
class Robot:
    def __init__(self):
        print("Robot físico inicializado.")

    def mover_servo(self, id, angulo):
        print(f"Servo {id} movido a {angulo}°")

    def mover_todo(self, base, hombro, codo, muneca):
        print(f"Moviendo servos: Base={base}, Hombro={hombro}, Codo={codo}, Muñeca={muneca}")
        self.mover_servo(1, base)
        self.mover_servo(2, hombro)
        self.mover_servo(3, codo)
        self.mover_servo(4, muneca)

# ======================================
# CLASE PRINCIPAL DE LA GUI
# ======================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control y Simulación del Robot 2D")
        self.setGeometry(200, 100, 900, 700)

        self.robot = Robot()

        # --- Layout principal ---
        layout_principal = QVBoxLayout()

        # --- Sliders ---
        self.sliders = []
        self.labels = []
        nombres = ["Base", "Hombro", "Codo", "Muñeca"]

        for nombre in nombres:
            layout_fila = QHBoxLayout()
            label = QLabel(f"{nombre}: 0°")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(180)
            slider.setValue(0)

            # Actualiza simulación mientras se mueve
            slider.valueChanged.connect(self.actualizar_simulacion_rapida)
            # Actualiza robot físico cuando se suelta el slider
            slider.sliderReleased.connect(self.actualizar_robot)

            layout_fila.addWidget(label)
            layout_fila.addWidget(slider)
            layout_principal.addLayout(layout_fila)
            self.sliders.append(slider)
            self.labels.append(label)

        # --- Botones ---
        botones_layout = QHBoxLayout()
        btn_abrir = QPushButton("Abrir")
        btn_cerrar = QPushButton("Cerrar")
        btn_abrir.clicked.connect(lambda: self.robot.mover_servo(5, 0))
        btn_cerrar.clicked.connect(lambda: self.robot.mover_servo(5, 90))
        botones_layout.addWidget(btn_abrir)
        botones_layout.addWidget(btn_cerrar)
        layout_principal.addLayout(botones_layout)

        # --- Simulación 2D ---
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout_principal.addWidget(self.canvas)

        # Inicializar líneas y puntos sin redibujar todo
        self.linea_robot, = self.ax.plot([], [], '-o', linewidth=3, markersize=8)
        self.ax.set_xlim(-0.3, 0.3)
        self.ax.set_ylim(-0.05, 0.3)
        self.ax.set_aspect('equal', 'box')
        self.ax.set_title("Simulación 2D del Robot (Vista XY)")
        self.ax.grid(True)

        # --- Configurar ventana ---
        widget = QWidget()
        widget.setLayout(layout_principal)
        self.setCentralWidget(widget)

        # Dibujar estado inicial
        self.actualizar_simulacion_rapida()

    # =============================
    # ACTUALIZAR ROBOT (solo físico)
    # =============================
    def actualizar_robot(self):
        angulos = [slider.value() for slider in self.sliders]
        self.robot.mover_todo(*angulos)
        self.actualizar_etiquetas(angulos)

    # =============================
    # ACTUALIZAR SIMULACIÓN RÁPIDA (solo gráfica)
    # =============================
    def actualizar_simulacion_rapida(self):
        angulos = [slider.value() for slider in self.sliders]
        self.actualizar_etiquetas(angulos)
        self.actualizar_simulacion(angulos)

    def actualizar_etiquetas(self, angulos):
        nombres = ["Base", "Hombro", "Codo", "Muñeca"]
        for i, label in enumerate(self.labels):
            label.setText(f"{nombres[i]}: {angulos[i]}°")

    # =============================
    # SIMULACIÓN 2D
    # =============================
    def actualizar_simulacion(self, angulos):
        # Longitudes
        L1, L2, L3, L4 = 0.1, 0.08, 0.06, 0.04
        rad = [math.radians(a) for a in angulos]

        x0, y0 = 0, 0
        x1 = L1 * math.cos(rad[0])
        y1 = L1 * math.sin(rad[0])
        x2 = x1 + L2 * math.cos(rad[0] + rad[1])
        y2 = y1 + L2 * math.sin(rad[0] + rad[1])
        x3 = x2 + L3 * math.cos(rad[0] + rad[1] + rad[2])
        y3 = y2 + L3 * math.sin(rad[0] + rad[1] + rad[2])
        x4 = x3 + L4 * math.cos(rad[0] + rad[1] + rad[2] + rad[3])
        y4 = y3 + L4 * math.sin(rad[0] + rad[1] + rad[2] + rad[3])

        self.linea_robot.set_data([x0, x1, x2, x3, x4],
                                  [y0, y1, y2, y3, y4])
        self.canvas.draw_idle()

# ======================================
# PROGRAMA PRINCIPAL
# ======================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
