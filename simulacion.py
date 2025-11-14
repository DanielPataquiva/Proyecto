import numpy as np
import roboticstoolbox as rtb
from spatialmath import SE3
import matplotlib.pyplot as plt


class RobotSimulation:
    def __init__(self):
        # Crear robot 4R
        self.robot = rtb.DHRobot([
            rtb.RevoluteDH(a=10, alpha=0),
            rtb.RevoluteDH(a=10, alpha=0),
            rtb.RevoluteDH(a=5, alpha=0),
            rtb.RevoluteDH(a=5, alpha=0)
        ], name="Bender")

        # Crear entorno PyPlot SOLO UNA VEZ
        self.env = rtb.backends.PyPlot.PyPlot()
        self.env.launch()

        # Limites del área
        self.env.ax.set_xlim([-20, 20])
        self.env.ax.set_ylim([-20, 20])
        self.env.ax.set_zlim([0, 25])

        # Agregar robot
        self.env.add(self.robot, readonly=True)

        print("Simulación lista")

    def update(self, angles_deg):
        """
        Actualiza la simulación con los nuevos ángulos.
        angles_deg: lista con 4 ángulos en grados
        """
        q_rad = np.radians(angles_deg)

        # Avanzar simulación
        try:
            self.env.step(q_rad)
        except Exception as e:
            print("Error en step:", e)


if __name__ == "__main__":
    sim = RobotSimulation()
    sim.update([0, 0, 0, 0])
