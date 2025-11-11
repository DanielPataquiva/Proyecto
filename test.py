from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)
ch = 0
try:
    while True:
        kit.servo[ch].angle = 0
        time.sleep(1)
        kit.servo[ch].angle = 180
        time.sleep(1)
except KeyboardInterrupt:
    kit.servo[ch].angle = 90
    print("Stopped")
