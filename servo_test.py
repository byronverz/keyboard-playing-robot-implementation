import Adafruit_BBIO.PWM as PWM

servo_pin = 'P9_16'

PWM.start(servo_pin, 10, 50)

def set_angle(duty_cycle):
    PWM.set_duty_cycle(servo_pin,duty_cycle)
    new_duty_cycle = input("New duty cycle: ")
    if new_duty_cycle == 'x':
        PWM.cleanup()
        return
    set_angle(int(new_duty_cycle))
    
    

set_angle(50)
        