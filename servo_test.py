import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO
import time
servo_pin = 'P9_16'
# GPIO.setup(servo_pin, GPIO.OUT)

# maximum = 0.0022
# minimum = 0.0008
# while True:
# GPIO.output(servo_pin,GPIO.HIGH)
# time.sleep(maximum)
# GPIO.output(servo_pin,GPIO.LOW)
PWM.start(servo_pin, 9, 200)

def set_angle(duty_cycle):
    PWM.set_duty_cycle(servo_pin,duty_cycle)
    new_duty_cycle = input("New duty cycle: ")
    if new_duty_cycle == 'x':
        PWM.cleanup()
        return
    set_angle(int(new_duty_cycle))
    
    
set_angle(40)        