import numpy as np
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time 
import qwiic_vl53l1x
import random


class Gantry:
    def __init__(self, calibrate_k = 1, sensor_address = 0x29, stepper_pwm = 'P8_13', en_pin = 'P8_7', dir_pin = 'P8_8', servo='P9_14'):
        self.calibration_key = calibrate_k
        self.previous_key = 0
        self.mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = sensor_address)
        self.mySensor.sensor_init()
        self.pwm_pin = stepper_pwm
        self.enable = en_pin
        self.direction = dir_pin
        self.servo_pin = servo
        self.home_set_point = 500.0   #make this a calculation from key to distance
        self.max_freq = 1000.0
        self.last = 0
        self.up_angle = 0.0008
        self.press_angle = 0.0022
        
        GPIO.setup(self.direction, GPIO.OUT)
        GPIO.setup(self.enable, GPIO.OUT)

        GPIO.output(self.enable,GPIO.LOW)
        PWM.start(self.servo_pin,6,50)

        print(self.mySensor.sensor_init())
        if (self.mySensor.sensor_init() == None):
            print("Sensor online")
        self.mySensor.set_distance_mode(2)
        self.mySensor.set_roi(8,8)
        home_bool = input("Would you like to home the gantry? (y/n)")
        if home_bool == 'y':
            self.auto_home(self.home_set_point, self.mySensor)
            return
        else: 
            return
        
    def auto_home(self, home_key, mySensor):
        self.mySensor.start_ranging()
        sensor_distance = self.mySensor.get_distance()
        self.mySensor.stop_ranging()
        print("Sensor distance: {}".format(sensor_distance))
        # if sensor_distance > home_key:
            # GPIO.output(self.direction, GPIO.LOW)
            # self.step_function(home_key, sensor_distance)
        # elif sensor_distance < home_key:
            # GPIO.output(self.direction, GPIO.HIGH)
        self.step_function(home_key, sensor_distance )
        print("Homing done!")
        # self.last = home_key
            
            
    def step_function(self,set_point, distance):
        prev_freq = 0
        error = distance - set_point
        frequency = self.max_freq*np.tanh(np.abs(error))
        print("Error: {}\tFrequency: {}".format(error,frequency))
        if error<0:
            print("Moving right")
            GPIO.output(self.direction, GPIO.LOW)
        elif error>0:
            print("Moving left")
            GPIO.output(self.direction, GPIO.HIGH)
        if (np.abs(prev_freq-frequency))>2000.0:
            # print("Stepping at half max_freq")
            PWM.start(self.pwm_pin,50,frequency/2)
            # PWM.set_frequency(self.pwm_pin, frequency/2)
        else:
            # print("Stepping at max_freq")
            PWM.start(self.pwm_pin,50,frequency)
            # PWM.set_frequency(self.pwm_pin, frequency)
            
        while np.abs(error) > 5.0:
            self.mySensor.start_ranging()
            time.sleep(0.015)
            distance = self.mySensor.get_distance()
            # time.sleep(0.005)
            self.mySensor.stop_ranging()
            print("Distance:\t{}".format(distance))
            error = distance - set_point
            frequency = self.max_freq*np.tanh(0.008*np.abs(error))
            try:
                PWM.set_frequency(self.pwm_pin, frequency)
            except:
                PWM.stop(self.pwm_pin)
        
        PWM.stop(self.pwm_pin)
        self.last = set_point
        
        
    def press_key(self, duration):
        PWM.set_duty_cycle(self.servo_pin,2)
        time.sleep(duration)
        PWM.set_duty_cycle(self.servo_pin,11)
        
        
    def distance_to_move_calc(self,key_list):
        # prev_set = self.last
        distance_to_move = []
        # direction = []
        for k in key_list:
            temp = (k*22.5)+100
            distance_to_move.append(temp)
            # self.prev_set = temp
        return distance_to_move
        
            
            
def main():
    g = Gantry()
    # keys = random.sample(range(1,25), 10)
    # keys = [1,25,2,24,3,23,4,22,5,21,6,20,7,19,8,18,9,17,10,16,11,15,12,14,13]
    # dist_arr = g.distance_to_move_calc(keys)
    # print("Keys: {}\t Distances:{}\t".format(keys,dist_arr))
    while True:
        g.mySensor.start_ranging()
        time.sleep(.005)
        sensor_distance = g.mySensor.get_distance()
        time.sleep(.005)
        g.mySensor.stop_ranging()
        d = input("Distance to move to?:")
        g.step_function(float(d),sensor_distance)
        g.press_key(0.25)

    
    # for d,k in zip(dist_arr,keys):
        # print("Key: {} \t Distance: {}".format(k,d))
        # g.mySensor.start_ranging()
        # sensor_distance = g.mySensor.get_distance()
        # g.mySensor.stop_ranging()
        # g.step_function(d,sensor_distance)
if __name__ == "__main__":
    main()
               
        
             