import numpy as np
from spatialmath.base import tr2rpy
from roboticstoolbox import DHRobot, RevoluteDH


class SimuladorRobot:
    def __init__(self):
        # Definición de parámetros DH (base rotacional)
        # L1: rotación alrededor del eje Z → α=90° mueve el plano del brazo
        L1 = RevoluteDH(a=0, alpha=np.pi/2, d=0, offset=0)   # base giratoria
        L2 = RevoluteDH(a=9, alpha=0, d=0, offset=0)        # primer brazo
        L3 = RevoluteDH(a=9, alpha=0, d=0, offset=0)        # segundo brazo
        L4 = RevoluteDH(a=9, alpha=0, d=0, offset=0)        # muñeca

        # Crear robot con los 4 eslabones
        self.robot = DHRobot([L1, L2, L3, L4], name="Bender_4R")
        self.q = [0, 0, 0, 0]
        self.actualizacion_contador = 0

        print("SimuladorRobot con base rotacional listo ✅")
        print(self.robot)

    def actualizar(self, angulos):
        """Actualiza la simulación (no en cada frame)"""
        self.q = np.radians(angulos)

        self.actualizacion_contador += 1
        if self.actualizacion_contador % 5 != 0:
            return

        MTH = self.robot.fkine(self.q)

        try:
            rpy = tr2rpy(MTH.R, order='zyx', unit='deg')
            print(f"Posición: {np.round(MTH.t, 2)} | RPY: {np.round(rpy, 2)}")
        except Exception as e:
            print(f"⚠️ Error RPY: {e}")

        try:
            self.robot.plot(
                self.q,
                block=False,
                limits=[-40, 40, -40, 40, 0, 50],
                jointaxes=False,
                eeframe=True,
                shadow=False,
                backend='pyplot'
            )
        except Exception as e:
            print(f"⚠️ Error gráfico: {e}")
