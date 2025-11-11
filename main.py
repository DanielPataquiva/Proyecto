import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5 import uic
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from robot import Robot


# ======================================
# CLASE PRINCIPAL
# ======================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("interface.ui", self)
        self.setWindowTitle("Control y Simulación 2D del Robot")

        # --- Instancia del robot físico ---
        self.robot = Robot()

        # --- Inicializar sliders ---
        self.sliders = [
            self.slider_base,
            self.slider_hombro,
            self.slider_codo,
            self.slider_muneca
        ]

        for s in self.sliders:
            s.setMinimum(0)
            s.setMaximum(180)
            s.setValue(0)
            s.valueChanged.connect(self.actualizar_robot)

        # --- Botones de la pinza ---
        self.btn_pick.clicked.connect(self.pick)
        self.btn_place.clicked.connect(self.place)

        # --- Configurar simulación 2D ---
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout_sim.addWidget(self.canvas)

        # --- Inicialización ---
        self.actualizar_robot()

    # =============================
    # ACCIONES DE BOTONES
    # =============================
    def pick(self):
        self.robot.pick()
        self.slider_pinza.setValue(0)

    def place(self):
        self.robot.place()
        self.slider_pinza.setValue(180)

    # =============================
    # ACTUALIZAR ROBOT
    # =============================
    def actualizar_robot(self):
        # Leer valores de sliders
        angulos = [s.value() for s in self.sliders]
        base, hombro, codo, muneca = angulos

        # Actualizar texto
        texto = (
            f"Base: {base}°\n"
            f"Hombro: {hombro}°\n"
            f"Codo: {codo}°\n"
            f"Muñeca: {muneca}°"
        )
        self.txt_angulos.setPlainText(texto)

        # Mover robot físico
        self.robot.mover_servos(base, hombro)
        self.robot.mover_codo(codo)
        self.robot.mover_muneca(muneca)

        # Actualizar simulación
        self.actualizar_simulacion(angulos)

    # =============================
    # SIMULACIÓN 2D
    # =============================
    def actualizar_simulacion(self, angulos):
        L1, L2, L3, L4 = 0.1, 0.08, 0.06, 0.04
        rad = [math.radians(a) for a in angulos]

        # Calcular posiciones de las articulaciones
        x0, y0 = 0, 0
        x1 = L1 * math.cos(rad[0])
        y1 = L1 * math.sin(rad[0])
        x2 = x1 + L2 * math.cos(rad[0] + rad[1])
        y2 = y1 + L2 * math.sin(rad[0] + rad[1])
        x3 = x2 + L3 * math.cos(rad[0] + rad[1] + rad[2])
        y3 = y2 + L3 * math.sin(rad[0] + rad[1] + rad[2])
        x4 = x3 + L4 * math.cos(rad[0] + rad[1] + rad[2] + rad[3])
        y4 = y3 + L4 * math.sin(rad[0] + rad[1] + rad[2] + rad[3])

        # --- Dibujar robot ---
        self.ax.clear()
        self.ax.plot([x0, x1, x2, x3, x4],
                     [y0, y1, y2, y3, y4],
                     '-o', linewidth=3, markersize=8, color='blue')

        # Etiquetas
        joints = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        for i, (x, y) in enumerate(joints[:-1]):
            self.ax.text(x, y + 0.015, f"θ{i+1}={angulos[i]}°",
                         fontsize=8, ha='center', color='red', weight='bold')

        # Ajustes visuales
        self.ax.set_xlim(-0.3, 0.3)
        self.ax.set_ylim(-0.05, 0.3)
        self.ax.set_aspect('equal', 'box')
        self.ax.set_title("Simulación 2D del Robot (Vista XY)")
        self.ax.grid(True)
        self.canvas.draw()


# ======================================
# PROGRAMA PRINCIPAL
# ======================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
