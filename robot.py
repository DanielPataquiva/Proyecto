# robot.py
import time
import math
import numpy as np

# Intentamos importar ServoKit; si falla, creamos una clase dummy para simular (útil para pruebas sin hardware)
try:
    from adafruit_servokit import ServoKit
    _HAS_SERVOKIT = True
except Exception:
    _HAS_SERVOKIT = False

# Intentamos usar Robotics Toolbox de Peter Corke; si no está, usaremos el fallback.
try:
    import roboticstoolbox as rtb
    from spatialmath import SE3
    _HAS_RTB = True
except Exception:
    _HAS_RTB = False

# Matplotlib para la simulación (embedding)
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure

class Robot:
    def __init__(self, use_physical=True, transition_delay=0.004):
        self.use_physical = use_physical and _HAS_SERVOKIT
        self.transition_delay = transition_delay

        # Mapeo de canales PCA9685 (físicos)
        # base=0, hombro_izq=1, hombro_der=2, codo=3, muneca=4, pinza=5
        self.servos = {
            "base": 0,
            "hombro_1": 1,
            "hombro_2": 2,
            "codo": 3,
            "muneca": 4,
            "pinza": 5
        }

        # Inicializar hardware si está disponible
        if self.use_physical:
            self.kit = ServoKit(channels=16)
            # Ajustar pulse width si lo necesitas
            for ch in self.servos.values():
                try:
                    self.kit.servo[ch].set_pulse_width_range(500, 2500)
                    self.kit.servo[ch].actuation_range = 180
                except Exception:
                    pass
        else:
            self.kit = None

        # Estados actuales (en grados)
        # Nota: en la interfaz manejamos 5 sliders: base, hombro, codo, muneca, pinza
        self.angles = {
            "base": 90,
            "hombro": 90,
            "codo": 90,
            "muneca": 90,
            "pinza": 90
        }

        # Parámetros de la geometría (longitudes arbitrarias, ajusta a tu robot)
        # Estos son para la simulación visual
        self.link_lengths = [0.12, 0.18, 0.14, 0.08]  # distancia entre articulaciones (m)

        # Preparar objeto de simulación (fallback)
        self.fig = None
        self.ax = None
        self._rtb_robot = None
        if _HAS_RTB:
            # Intentamos crear un modelo DH simple con 5 DOF (base, hombro, codo, muneca, pinza)
            try:
                # Ejemplo rápido: usar parámetros DH simples; ajústalos a tu robot si quieres mayor realismo
                L0 = rtb.RevoluteDH(d=0, a=0, alpha=math.pi/2)   # base rot Z
                L1 = rtb.RevoluteDH(d=0, a=self.link_lengths[0], alpha=0)  # hombro
                L2 = rtb.RevoluteDH(d=0, a=self.link_lengths[1], alpha=0)  # codo
                L3 = rtb.RevoluteDH(d=0, a=self.link_lengths[2], alpha=0)  # muneca
                L4 = rtb.RevoluteDH(d=0, a=self.link_lengths[3], alpha=0)  # efector (pinza)
                self._rtb_robot = rtb.DHRobot([L0, L1, L2, L3, L4], name="brazo_simple")
            except Exception:
                self._rtb_robot = None

    # ---------- Hardware movement ----------
    def _move_physical_servo(self, ch, ang):
        if not self.use_physical:
            return
        try:
            self.kit.servo[ch].angle = ang
        except Exception as e:
            print(f"Error moviendo servo canal {ch}: {e}")

    def mover_servo(self, nombre, angulo):
        """
        Mueve servo/s según nombre:
        - 'hombro' mueve ambos canales hombro_1 y hombro_2 sincronizados
        - otros nombres mueven el canal correspondiente
        """
        if nombre == "hombro":
            # sincroniza dos servos
            chs = [self.servos["hombro_1"], self.servos["hombro_2"]]
            actual = self.angles["hombro"]
            objetivo = int(angulo)
            if objetivo == actual:
                return
            paso = 1 if objetivo > actual else -1
            for a in range(actual, objetivo, paso):
                for ch in chs:
                    self._move_physical_servo(ch, a)
                time.sleep(self.transition_delay)
            for ch in chs:
                self._move_physical_servo(ch, objetivo)
            self.angles["hombro"] = objetivo
        else:
            # nombre entre base, codo, muneca, pinza
            if nombre not in self.angles:
                print(f"Servo desconocido para mover: {nombre}")
                return
            actual = self.angles[nombre]
            objetivo = int(angulo)
            if objetivo == actual:
                return
            paso = 1 if objetivo > actual else -1
            ch = self.servos.get(nombre if nombre != "pinza" else "pinza")
            for a in range(actual, objetivo, paso):
                if self.use_physical and ch is not None:
                    self._move_physical_servo(ch, a)
                time.sleep(self.transition_delay)
            if self.use_physical and ch is not None:
                self._move_physical_servo(ch, objetivo)
            self.angles[nombre] = objetivo

        # después de mover, actualizar simulación (si está inicializada)
        if self.fig is not None:
            self.update_simulation()

        # imprimir en consola también (como pedías antes)
        self._print_angles_console()

    def set_servo_direct(self, nombre, angulo):
        """Mover sin interpolación (directo)"""
        if nombre == "hombro":
            chs = [self.servos["hombro_1"], self.servos["hombro_2"]]
            for ch in chs:
                if self.use_physical:
                    self._move_physical_servo(ch, angulo)
            self.angles["hombro"] = angulo
        else:
            ch = self.servos.get(nombre)
            if self.use_physical and ch is not None:
                self._move_physical_servo(ch, angulo)
            self.angles[nombre] = angulo
        if self.fig is not None:
            self.update_simulation()
        self._print_angles_console()

    def pick(self):
        # cerrar pinza a 0°
        self.mover_servo("pinza", 0)

    def place(self):
        # abrir pinza a 180°
        self.mover_servo("pinza", 180)

    def _print_angles_console(self):
        # Imprime ángulos por articulación
        print("Ángulos actuales:")
        for k, v in self.angles.items():
            print(f"  {k}: {v}°")

    # ---------- Simulación: inicializar canvas ----------
    def init_simulation_canvas(self, fig, ax):
        """
        Debes pasar un matplotlib.figure.Figure y su ax (Axes3D) para que el Robot
        pueda dibujar dentro.
        """
        self.fig = fig
        self.ax = ax
        # configurar ejes
        self.ax.clear()
        self.ax.set_box_aspect([1,1,0.6])
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.view_init(elev=30, azim=45)
        self._draw_base()
        self.fig.canvas.draw_idle()

    def _draw_base(self):
        # dibuja un punto base
        self.ax.scatter([0], [0], [0], c='k', s=20)

    def update_simulation(self):
        """
        Actualiza la simulación 3D en el axes dado con los ángulos actuales.
        Si roboticstoolbox está disponible se intentará usarlo; si no, se usa FK simple.
        """
        if self.fig is None or self.ax is None:
            return

        self.ax.cla()
        self._draw_base()
        # coordenadas del eslabón (origen)
        origin = np.array([0.0, 0.0, 0.0])

        # convertimos ángulos a radianes y definimos transformaciones simples
        # defino: base: rotZ, hombro: rotY, codo: rotY, muneca: rotY
        b = math.radians(self.angles["base"] - 90)   # centramos 90° -> 0 rad
        s = math.radians(self.angles["hombro"] - 90)
        e = math.radians(self.angles["codo"] - 90)
        w = math.radians(self.angles["muneca"] - 90)

        # matrices de rotación y transformaciones simples
        def Rz(theta):
            return np.array([[math.cos(theta), -math.sin(theta), 0],
                             [math.sin(theta),  math.cos(theta), 0],
                             [0, 0, 1]])
        def Ry(theta):
            return np.array([[ math.cos(theta), 0, math.sin(theta)],
                             [0, 1, 0],
                             [-math.sin(theta),0, math.cos(theta)]])

        # Link vectors (en coordenadas locales)
        L = self.link_lengths
        p0 = origin
        # base a hombro
        p1 = p0 + Rz(b).dot(np.array([0, 0, 0]))  # base solo rota en Z (origen compartido)
        # hombro
        p2 = p1 + Rz(b).dot(Ry(s).dot(np.array([L[0], 0, 0])))
        # codo
        p3 = p2 + Rz(b).dot(Ry(s).dot(Ry(e).dot(np.array([L[1], 0, 0]))))
        # muneca
        p4 = p3 + Rz(b).dot(Ry(s).dot(Ry(e).dot(Ry(w).dot(np.array([L[2], 0, 0])))))
        # efector final
        p5 = p4 + Rz(b).dot(Ry(s).dot(Ry(e).dot(Ry(w).dot(np.array([L[3], 0, 0])))))

        xs = [p0[0], p2[0], p3[0], p4[0], p5[0]]
        ys = [p0[1], p2[1], p3[1], p4[1], p5[1]]
        zs = [p0[2], p2[2], p3[2], p4[2], p5[2]]

        # dibujar líneas entre puntos
        self.ax.plot(xs, ys, zs, '-o', linewidth=4, markersize=6)
        # dibujar pinza como dos líneas pequeñas dependiendo del ángulo de pinza
        pinch = (self.angles["pinza"] - 90) / 90.0  # -1..1
        # vector lateral para pinza
        vlat = np.array([0, 0.02, 0])
        # lineas de la pinza
        p_left = p5 + Rz(b).dot(np.array([0, 0.01 + 0.02*pinch, 0]))
        p_right = p5 + Rz(b).dot(np.array([0, -0.01 - 0.02*pinch, 0]))
        self.ax.plot([p5[0], p_left[0]], [p5[1], p_left[1]], [p5[2], p_left[2]], '-', linewidth=3)
        self.ax.plot([p5[0], p_right[0]], [p5[1], p_right[1]], [p5[2], p_right[2]], '-', linewidth=3)

        # ajustes visuales
        all_x = xs + [p_left[0], p_right[0]]
        all_y = ys + [p_left[1], p_right[1]]
        all_z = zs + [p_left[2], p_right[2]]
        # set limits
        margin = 0.05
        self.ax.set_xlim(min(all_x)-margin, max(all_x)+margin)
        self.ax.set_ylim(min(all_y)-margin, max(all_y)+margin)
        self.ax.set_zlim(min(all_z)-margin, max(all_z)+margin)
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.view_init(elev=30, azim=45)
        self.fig.canvas.draw_idle()
