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

def press_key(angle):
    # s = time.time()
    PWM.set_duty_cycle(servo_pin,angle)
    time.sleep(1)
    PWM.set_duty_cycle(servo_pin,22)
    # print("Key pressed for {} seconds".format(time.time()-s))
    
 
io = 0.5
while io !='x':
    
    volume_adjust(float(io))
    # press_key(float(io))
    io = input("Angle: ")

PWM.cleanup()