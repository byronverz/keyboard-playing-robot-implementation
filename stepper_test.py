import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time 

DIR_PIN = 'P8_8'
EN_PIN = 'P8_7'
pwm_pin = 'P8_13'

GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN,GPIO.LOW)
GPIO.output(DIR_PIN,GPIO.HIGH)
PWM.start(pwm_pin,50,1000)
def step_speed_test (frequency, duty):
    print("Stepping at frequency {} Hz".format(frequency))
    PWM.set_frequency(pwm_pin,frequency)
    PWM.set_duty_cycle(pwm_pin, duty)
    # wait = 1/(2*frequency)
    end_time = 0.0
    # while (end_time-start_time) < 5.0:
        # end_time = time.time()    
        # GPIO.output(pin, GPIO.HIGH)
        # time.sleep(wait)
        # GPIO.output(pin, GPIO.LOW)
        # time.sleep(wait)
    new_frequency = input("New frequency? :")
    # new_frequency = 1000
    new_duty = input("New duty? :")
    if (new_frequency ) == 'x':
        PWM.stop(pwm_pin)
        PWM.cleanup()
        return
    step_speed_test(int(new_frequency), int(new_duty))
    
    
def main():
    step_speed_test(1000, 50)
    
if __name__ == "__main__":
    main()
    
 