import Adafruit_BBIO.GPIO as GPIO
import time 

pin = 'P8_7'

GPIO.setup(pin, GPIO.OUT)

def step_speed_test (frequency):
    print("Stepping at frequency {} Hz".format(frequency))
    wait = 1/(2*frequency)
    while True:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(wait)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(wait)
        
def main():
    step_speed_test(1000)
    
if __name__ == "__main__":
    main()
    
 