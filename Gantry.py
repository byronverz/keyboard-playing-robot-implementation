import numpy as np
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time 
import qwiic_vl53l1x


class Gantry:
    def __init__(self, calibrate_k = 1, sensor_address = 0x29, stepper_pwm = 'P8_13', en_pin = 'P8_7', dir_pin = 'P8_8'):
        self.calibration_key = calibrate_k
        self.previous_key = 0
        self.mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = sensor_address)
        self.mySensor.sensor_init()
        self.pwm_pin = stepper_pwm
        self.enable = en_pin
        self.direction = dir_pin
        self.home_set_point = 30.0   #make this a calculation from key to distance
        self.max_freq = 4000.0
        
        GPIO.setup(self.direction, GPIO.OUT)
        GPIO.setup(self.enable, GPIO.OUT)
        GPIO.output(self.enable,GPIO.LOW)
        
        self.mySensor.set_distance_mode(1)
        print(self.mySensor.sensor_init())
        if (self.mySensor.sensor_init() == None):
            print("Sensor online")
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
        if sensor_distance > home_key:
            GPIO.output(self.direction, GPIO.LOW)
            self.step_function(home_key, sensor_distance)
        elif sensor_distance < home_key:
            GPIO.output(self.direction, GPIO.HIGH)
            self.step_function(home_key, sensor_distance )
            
            
            
    def step_function(self,set_point, distance):
        prev_freq = 0
        error = distance - set_point
        frequency = self.max_freq*np.tanh(error)
        if (np.abs(prev_freq-frequency))>2000.0:
            PWM.start(self.pwm_pin,50,frequency/2)
            # PWM.set_frequency(self.pwm_pin, frequency/2)
        else:
            PWM.start(self.pwm_pin,50,frequency)
            # PWM.set_frequency(self.pwm_pin, frequency)
            
        while error > 5.0:
            self.mySensor.start_ranging()
            time.sleep(0.005)
            distance = self.mySensor.get_distance()
            time.sleep(0.005)
            self.mySensor.stop_ranging()
            error = distance - set_point
            frequency = self.max_freq*np.tanh(0.008*error)
            try:
                PWM.set_frequency(self.pwm_pin, frequency)
            except:
                PWM.stop(self.pwm_pin)
        
        PWM.stop(self.pwm_pin)
        print("Homing done!")
            
            
def main():
    g = Gantry()
    
if __name__ == "__main__":
    main()
               
        
             