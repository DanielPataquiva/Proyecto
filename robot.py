import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import math

# =============================
# Parámetros del robot
# =============================
l1 = 10
l2 = 10
l3 = 10
l4 = 10

# =============================
# Función de cinemática directa
# =============================
def cinematica_directa(q):
    q1, q2, q3, q4 = np.deg2rad(q)

    x0, y0 = 0, 0
    x1 = l1 * np.cos(q1)
    y1 = l1 * np.sin(q1)

    x2 = x1 + l2 * np.cos(q1 + q2)
    y2 = y1 + l2 * np.sin(q1 + q2)

    x3 = x2 + l3 * np.cos(q1 + q2 + q3)
    y3 = y2 + l3 * np.sin(q1 + q2 + q3)

    x4 = x3 + l4 * np.cos(q1 + q2 + q3 + q4)
    y4 = y3 + l4 * np.sin(q1 + q2 + q3 + q4)

    X = [x0, x1, x2, x3, x4]
    Y = [y0, y1, y2, y3, y4]

    return X, Y, x4, y4  # también retorna el efector final

# =============================
# Inicialización
# =============================
q_init = [90, 90, 90, 90]  # todos al centro del rango
X, Y, xe, ye = cinematica_directa(q_init)

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, bottom=0.35)
ax.set_aspect('equal')
ax.set_xlim(-50, 50)
ax.set_ylim(-10, 50)
ax.grid(True)

# Dibujo del robot
line, = ax.plot(X, Y, 'o-', lw=3, color='royalblue')

# Texto para mostrar coordenadas (x, y)
pos_text = ax.text(-45, 45, f'X = {xe:.2f}   Y = {ye:.2f}', fontsize=10,
                   bbox=dict(facecolor='white', alpha=0.7))

# =============================
# Sliders (0° a 180°)
# =============================
axcolor = 'lightgoldenrodyellow'
slider1_ax = plt.axes([0.15, 0.25, 0.65, 0.03], facecolor=axcolor)
slider2_ax = plt.axes([0.15, 0.20, 0.65, 0.03], facecolor=axcolor)
slider3_ax = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor=axcolor)
slider4_ax = plt.axes([0.15, 0.10, 0.65, 0.03], facecolor=axcolor)

slider1 = Slider(slider1_ax, 'θ1', 0, 180, valinit=q_init[0])
slider2 = Slider(slider2_ax, 'θ2', 0, 180, valinit=q_init[1])
slider3 = Slider(slider3_ax, 'θ3', 0, 180, valinit=q_init[2])
slider4 = Slider(slider4_ax, 'θ4', 0, 180, valinit=q_init[3])

# =============================
# Actualización en tiempo real
# =============================
def update(val):
    q = [slider1.val, slider2.val, slider3.val, slider4.val]
    X, Y, xe, ye = cinematica_directa(q)
    line.set_data(X, Y)
    pos_text.set_text(f'X = {xe:.2f}   Y = {ye:.2f}')
    fig.canvas.draw_idle()

slider1.on_changed(update)
slider2.on_changed(update)
slider3.on_changed(update)
slider4.on_changed(update)

plt.show()
