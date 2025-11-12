import numpy as np
from spatialmath import SE3
from spatialmath.base import tr2rpy
from roboticstoolbox import DHRobot, RevoluteDH
import roboticstoolbox as rtb


class SimuladorRobot:
    def __init__(self):
        # Definición de parámetros DH (puedes ajustar según tu robot)
        L1 = RevoluteDH(a=10, alpha=0, d=0, offset=0)
        L2 = RevoluteDH(a=10, alpha=0, d=0, offset=0)
        L3 = RevoluteDH(a=10, alpha=0, d=0, offset=0)
        L4 = RevoluteDH(a=10, alpha=0, d=0, offset=0)

        # Crear el robot con los 4 eslabones
        self.robot = DHRobot([L1, L2, L3, L4], name="Bender_4R")

        # Posición inicial (todos los ángulos en 0)
        self.q = [0, 0, 0, 0]

        print("SimuladorRobot listo ✅")
        print(self.robot)

    def actualizar(self, angulos):
        """
        Actualiza la simulación con los nuevos ángulos del robot.
        angulos: lista de 4 valores (en grados)
        """
        # Convertir grados a radianes
        self.q = np.radians(angulos)

        # Calcular la cinemática directa
        MTH = self.robot.fkine(self.q)
        print("\nNueva posición simulada:")
        print(np.round(MTH.A, 4))

        # Calcular e imprimir orientación RPY (orden zyx)
        try:
            rpy = tr2rpy(MTH.R, order='zyx', unit='deg')
            print(f"Roll, Pitch, Yaw = {np.round(rpy, 2)}")
        except Exception as e:
            print(f"⚠️ Error calculando RPY: {e}")

        # Actualizar la visualización 3D del robot
        try:
            # Límites corregidos: [xmin, xmax, ymin, ymax, zmin, zmax]
            self.robot.plot(
                self.q,
                block=False,
                limits=[-40, 40, -10, 40, 0, 50],
                jointaxes=False,
                eeframe=True,
                shadow=True
            )
        except Exception as e:
            print(f"⚠️ Error al graficar: {e}")
