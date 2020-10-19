import numpy as np
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time 

stepping_pin = "P8_9"
pwm_pin = "P9_14"
GPIO.setup(stepping_pin, GPIO.OUT)
print("Start stepping")
def step():
    for n in range(10000):
        GPIO.output(stepping_pin,GPIO.HIGH)
        # time.sleep(0.00005)
        GPIO.output(stepping_pin,GPIO.LOW)
        # time.sleep(0.00005)
while True:
    again = input("Send 10 000 steps?: ")
    if again == 'y':
        step()
    elif again == 'p':
        PWM.start(pwm_pin, 50, 2000)
    else:
        PWM.cleanup()
        break