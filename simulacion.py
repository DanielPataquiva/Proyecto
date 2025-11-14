import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

# ============================
# MODELO DEL ROBOT
# ============================

L1, L2, L3 = 9, 9, 9

links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),  # Base
    RevoluteDH(d=0, a=L1, alpha=0),              # Hombro
    RevoluteDH(d=0, a=L2, alpha=0),              # Codo
    RevoluteDH(d=0, a=L3, alpha=0)               # Muñeca
]

robot = DHRobot(links, name="Robot_4R")

# ============================
# FUNCIÓN PARA DIBUJAR BASE
# ============================

def draw_base(ax, size=8):
    """
    Dibuja una plataforma plana en el piso para representar la base del robot.
    """
    X = [-size, size, size, -size]
    Y = [-size, -size, size, size]
    Z = [0, 0, 0, 0]

    ax.plot_trisurf(X, Y, Z, color="gray", alpha=0.3)

# ============================
# SIMULACIÓN
# ============================

class Simulacion:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.show()

    def update(self, angles_deg):
        q_rad = np.deg2rad(angles_deg)

        plt.clf()

        # Crear un nuevo gráfico 3D
        ax = plt.gca(projection='3d')

        # ----------- AGREGAR BASE VISUAL -------------
        draw_base(ax)
        # ---------------------------------------------

        # Dibujar robot
        robot.plot(q_rad, block=False, limits=[-20, 20, -20, 20, 0, 25])

        plt.pause(0.001)
