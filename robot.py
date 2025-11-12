from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath.base import tr2rpy
import numpy as np
import matplotlib.pyplot as plt

class SimuladorRobot:
    def __init__(self):
        l1 = l2 = l3 = l4 = 10
        self.links = [
            RevoluteDH(a=l1, alpha=0),
            RevoluteDH(a=l2, alpha=0),
            RevoluteDH(a=l3, alpha=0),
            RevoluteDH(a=l4, alpha=0)
        ]
        self.robot = DHRobot(self.links, name='Bender_4R')

        # Configuración inicial (ángulos en radianes)
        self.q = [0, 0, 0, 0]

        print("\nSimuladorRobot listo ✅")
        print(self.robot)

    def actualizar(self, angulos):
        """Actualiza la simulación con nuevos ángulos (en grados)."""
        self.q = np.deg2rad(angulos)  # Convertir a radianes
        MTH = self.robot.fkine(self.q)
        print("\nNueva posición simulada:")
        print(MTH)
       # print(f"Roll, Pitch, Yaw = {np.round(tr2rpy(MTH.R, 'zyx', 'deg'), 2)}")
        print(f"Roll, Pitch, Yaw = {np.round(tr2rpy(MTH.R, unit='deg', order='zyx'), 2)}")

        # Dibujar 2D simple
        self.robot.plot(self.q, block=False, limits=[-40, 40, -10, 40])
        plt.pause(0.01)
