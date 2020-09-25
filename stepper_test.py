import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time 
import random
import numpy as np

DIR_PIN = 'P8_8'
EN_PIN = 'P8_7'
pwm_pin = 'P8_13'
# servo_1 = 'P8_13'
# servo_2 = 'P9_16'

GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN,GPIO.LOW)
GPIO.output(DIR_PIN,GPIO.HIGH)
PWM.start(pwm_pin,50,1000)
# PWM.start(servo_1,10,50)
# PWM.start(servo_2,10,50)
def step_speed_test (frequency, duty):
    print("Stepping at frequency {} Hz".format(frequency))
    PWM.set_frequency(pwm_pin,frequency)
    # PWM.set_duty_cycle(pwm_pin, duty)
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

def rail_test(time_to_switch, frequency):
    PWM.start(pwm_pin,50,frequency)
    time.sleep(time_to_switch)
    GPIO.output(DIR_PIN,GPIO.LOW)
    time.sleep(time_to_switch)
    GPIO.output(DIR_PIN,GPIO.HIGH)
    PWM.stop(pwm_pin)
    new_time = input("New time to switch: ")
    new_frequency = input("New frequency: ")
    if (new_time or new_frequency) == 'x':
        return
    rail_test(float(new_time), int(new_frequency))

def move(direction, time_to_move,frequency = 3500):
    if direction == 1:
        GPIO.output(DIR_PIN,GPIO.HIGH)
    elif direction ==0:
        GPIO.output(DIR_PIN,GPIO.LOW)
    else:
        print('No direction given')
        return
    PWM.start(pwm_pin,50,frequency)
    time.sleep(time_to_move)
    PWM.stop(pwm_pin)
    # new_dir = input("New direction:  (1 - Left, 0 - Right) ")
    # new_time= input("New time to move: ")
    # new_frequency = input("New frequency: ")
    # if (new_dir or new_time) == 'x':
        # return
    # move(int(new_dir), float(new_time), int(new_frequency))

def time_to_move_calc(key_list):
    prev_key = 25
    time = []
    direction = []
    for k in key_list:
        temp = (prev_key - k)/44
        time.append(temp)
        if temp<0:
            direction.append(0)
        elif temp>0:
            direction.append(1)
        prev_key = k
    return direction, np.abs(time)
    
    
def main():
    time.sleep(2)
    keys = random.sample(range(1,25), 10)
    keys.append(25)
    direction, time_arr = time_to_move_calc(keys)
    for d, t in zip(direction, time_arr):
        print("Direction: {} \t Time: {}".format(d,t))
        # move(d,t)
    # print(keys)
    step_speed_test(1000, 50)
    # rail_test(1,100)
    # move(0,1.5,250)
    PWM.cleanup()
    
if __name__ == "__main__":
    main()
    
 