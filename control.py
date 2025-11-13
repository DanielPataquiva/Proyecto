from adafruit_servokit import ServoKit

# ============================
# CONFIGURACIÓN PCA9685 Y SERVOS
# ============================

kit = ServoKit(channels=16)

for ch in range(6):
    kit.servo[ch].set_pulse_width_range(500, 2500)

servo_config = {
    0: {"offset": 0,  "invert": False},   # Base
    1: {"offset": 0,  "invert": False},   # Hombro A
    2: {"offset": 0,  "invert": True},    # Hombro B
    3: {"offset": 0,  "invert": False},   # Codo
    4: {"offset": 0,  "invert": False},   # Muñeca
    5: {"offset": 0,  "invert": False},   # Pinza
}

# ============================
# FUNCIONES DE CONTROL DE SERVOS
# ============================

def set_servo_angle(channel, angle):
    cfg = servo_config[channel]
    offset, invert = cfg["offset"], cfg["invert"]
    adj_angle = angle + offset
    adj_angle = max(0, min(180, adj_angle))
    if invert:
        adj_angle = 180 - adj_angle
    kit.servo[channel].angle = adj_angle

def move_joint(index, angle):
    """Mapea índice de articulación a canal del servo físico"""
    if index == 0:
        set_servo_angle(0, angle)
    elif index == 1:
        set_servo_angle(1, angle)
        set_servo_angle(2, angle)
    elif index == 2:
        set_servo_angle(3, angle)
    elif index == 3:
        set_servo_angle(4, angle)

def pick():
    set_servo_angle(5, 0)

def place():
    set_servo_angle(5, 180)
