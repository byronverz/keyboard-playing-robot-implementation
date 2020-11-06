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
PWM.start(servo_pin, 31, 200)

        
def volume_adjust(v):
    dc = -35*v+49
    PWM.set_duty_cycle(servo_pin,dc)
    print("Volume set")
        
 
io = 0.5
while io !='x':
    
    volume_adjust(float(io))
    io = input("Volume: ")