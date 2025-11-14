import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D projection)

# ============================
# MODELO DEL ROBOT (misma definición que en main)
# ============================

L1, L2, L3 = 9, 9, 9

links = [
    RevoluteDH(d=0, a=0, alpha=np.deg2rad(90)),  # Base
    RevoluteDH(d=0, a=L1, alpha=0),              # Hombro
    RevoluteDH(d=0, a=L2, alpha=0),              # Codo
    RevoluteDH(d=0, a=L3, alpha=0)               # Muñeca
]

robot = DHRobot(links, name="Robot_4R")

# Aseguramos que la base del robot esté en el origen (matriz identidad)
robot.base = np.eye(4)

# ============================
# FUNCIÓN PARA DIBUJAR BASE
# ============================

def draw_base(ax, size=6, height=0.5):
    """
    Dibuja una plataforma rectangular (base) centrada en el origen.
    size: semilado en unidades (la plataforma irá de -size a +size en X e Y)
    height: altura (z) de la plataforma (se dibuja una placa delgada)
    """
    # vértices de la placa en z=0
    X = np.array([-size, size, size, -size])
    Y = np.array([-size, -size, size, size])
    Z = np.zeros_like(X)

    # superficie (triángulos) para la placa
    verts = [list(zip(X, Y, Z))]
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    pc = Poly3DCollection(verts, alpha=0.25, facecolor='gray', edgecolor='k')
    ax.add_collection3d(pc)

    # opcional: dibujar un cilindro pequeño que represente el eje de giro (columna central)
    theta = np.linspace(0, 2 * np.pi, 30)
    r = size * 0.08
    z = np.linspace(0, height, 2)
    theta, z = np.meshgrid(theta, z)
    Xc = r * np.cos(theta)
    Yc = r * np.sin(theta)
    Zc = z
    ax.plot_surface(Xc, Yc, Zc, alpha=0.6, color='lightgray', linewidth=0)

# ============================
# SIMULACIÓN
# ============================

class Simulacion:
    def __init__(self):
        # Creamos figura y eje 3D una sola vez (mejor rendimiento y mantiene escala)
        self.fig = plt.figure(figsize=(6,6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        # Ajustes iniciales de vista
        self.ax.view_init(elev=20, azim=-60)
        self.fig.tight_layout()
        # Mostrar figura (dependiendo del entorno puede mostrarse automáticamente)
        plt.ion()
        self.fig.show()

    def update(self, angles_deg):
        """
        angles_deg: lista/array con los ángulos en grados [theta1, theta2, theta3, theta4]
        """
        q_rad = np.deg2rad(angles_deg)

        # Limpiar eje (no la figura completa)
        self.ax.cla()

        # Dibujar base en el origen
        draw_base(self.ax, size=6, height=0.8)

        # Forzar aspecto de caja uniforme para que X, Y, Z tengan la misma escala visual
        # Usamos set_box_aspect (disponible en matplotlib >= 3.3)
        try:
            self.ax.set_box_aspect([1, 1, 0.8])  # X:Y:Z ratio
        except Exception:
            # En versiones antiguas, se hace con límites manuales (fallback)
            pass

        # Etiquetas
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        # Límites centrados alrededor del origen para una vista equilibrada
        lim = 20
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)
        self.ax.set_zlim(0, 25)

        # Ajustar vista inicial (opcional, puedes cambiar elev/azim)
        self.ax.view_init(elev=25, azim=-50)

        # Dibujar robot en el eje existente.
        # roboticstoolbox admite pasar un `ax` para dibujar en ese Axes3D.
        # Usamos backend matplotlib (por defecto) y pasamos nuestro ax.
        robot.plot(q_rad, block=False, ax=self.ax, limits=[-lim, lim, -lim, lim, 0, 25])

        # Forzar redraw
        self.fig.canvas.draw()
        plt.pause(0.001)
