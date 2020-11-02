import numpy as np
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time 
import qwiic_vl53l1x
import random


class Gantry:
    def __init__(self, calibrate_k = 0, sensor_address = 0x29, stepper_pwm = 'P8_13', en_pin = 'P8_7', dir_pin = 'P8_8', finger_servo='P9_14', vol_servo = 'P9_16'):
        self.calibration_key = calibrate_k
        # self.previous_key = 0
        self.mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = sensor_address)
        self.mySensor.sensor_init()
        self.pwm_pin = stepper_pwm
        self.enable = en_pin
        self.direction = dir_pin
        self.finger_servo_pin = finger_servo
        self.vol_servo_pin = vol_servo
        self.home_set_point = 482.27+7   #make this a calculation from key to distance
        self.max_freq = 1500.0
        self.last = 0
        self.up_angle = 22
        self.press_angle = 16
        self.KEY_CONST = 13.25
        self.theta_m = 0.45*(np.pi/180)
        self.radius = 37.5
        self.freq_curve = [6, 342, 888, 1459 ,1947, 2308, self.max_freq]
        GPIO.setup(self.direction, GPIO.OUT)
        GPIO.setup(self.enable, GPIO.OUT)

        GPIO.output(self.enable,GPIO.LOW)
        PWM.start(self.finger_servo_pin,self.up_angle,200)
        PWM.start(self.vol_servo_pin,32,200)

        self.mySensor.sensor_init()
        if (self.mySensor.sensor_init() == None):
            print("Sensor online")
        else:
            print("ToF sensor error, reboot sensor")
            return
        self.mySensor.set_roi(8,8)
        self.mySensor.set_offset(23)
        self.mySensor.set_inter_measurement_in_ms(250)
        self.mySensor.set_timing_budget_in_ms(150)
        home_bool = input("Would you like to home the gantry? (y/n)")
        if home_bool == 'y':
            self.auto_home(self.home_set_point, self.mySensor)
            return
        else: 
            return
        
    def auto_home(self, home_key, mySensor):
        # self.mySensor.start_ranging()
        # time.sleep(0.01)
        # sensor_distance = self.mySensor.get_distance()
        # time.sleep(0.01)
        # self.mySensor.stop_ranging()
        # print("Sensor distance: {}".format(sensor_distance))
        # if sensor_distance > home_key:
            # GPIO.output(self.direction, GPIO.LOW)
            # self.step_function(home_key, sensor_distance)
        # elif sensor_distance < home_key:
            # GPIO.output(self.direction, GPIO.HIGH)
        d,f, e = self.step_function(home_key,0.5)
        print("Homing done!")
        self.previous_key = 0
            
            
    def step_function(self,set_point, k_time):
        self.mySensor.start_ranging()
        time.sleep(0.01)
        distance = self.mySensor.get_distance()
        time.sleep(0.01)
        self.mySensor.stop_ranging()
        
        dist_out = []
        freq_out = []
        error_out = []
        prev_freq = 0
        error = distance - set_point
        # frequency = self.max_freq*np.tanh(np.abs(error))
        frequency = np.abs(error)
        # print("Error: {}".format(error))
        if error<0:
            self.dir_bool = False
            # print("Moving right")
            GPIO.output(self.direction, GPIO.LOW)
        elif error>0:
            self.dir_bool = True
            # print("Moving left")
            GPIO.output(self.direction, GPIO.HIGH)
        if (np.abs(prev_freq-frequency))>2000.0:
            try:
                PWM.start(self.pwm_pin,50,frequency/2)
            except:
                pass
        else:
            try:
                PWM.start(self.pwm_pin,50,frequency)
            except:
                print("Stepper PWM failed to start")
                pass
        error_sum = 0 
        while np.abs(error) > 1.0:
            dist_out.append(distance)
            freq_out.append(frequency)
            error_out.append(error)
            self.mySensor.start_ranging()
            time.sleep(0.01)
            distance = self.mySensor.get_distance()
            time.sleep(0.01)
            self.mySensor.stop_ranging()
            error = distance - set_point
            error_sum += error
            # print("Error:\t{}".format(error))
            sign = self.sign_to_bool(error)
            if sign != self.dir_bool:
                self.dir_bool = not self.dir_bool
                if error<0:
                    GPIO.output(self.direction, GPIO.LOW)
                elif error>0:
                    GPIO.output(self.direction, GPIO.HIGH)
            # frequency = self.max_freq*np.tanh(0.008*np.abs(error))
            # frequency = np.abs
            frequency = 7*error+(0.025/3)*error_sum
            # print(frequency)
            try:
                PWM.set_frequency(self.pwm_pin, np.abs(frequency))
            except:
                PWM.stop(self.pwm_pin)
        
        PWM.stop(self.pwm_pin)
        self.last = set_point
        self.press_key(k_time)
        return np.array(dist_out), np.array(freq_out), np.array(error_out)
    
    
    def sign_to_bool(self, in_var):
        if in_var<0:
            return False
        elif in_var>0:
            return True
        
        
    def press_key(self, duration):
        # s = time.time()
        PWM.set_duty_cycle(self.finger_servo_pin,self.press_angle)
        time.sleep(duration)
        PWM.set_duty_cycle(self.finger_servo_pin,self.up_angle)
        # print("Key pressed for {} seconds".format(time.time()-s))
        
        
    def volume_adjust(self, v):
        dc = -35*v+49
        PWM.set_duty_cycle(self.vol_servo_pin,dc)
        print("Volume set")
        
        
    def distance_to_move_calc(self,key_list):
        # prev_set = self.last
        distance_to_move = []
        # direction = []
        for k in key_list:
            distance_to_move.append(19.93715*k+476.26455)
            # self.prev_set = temp
        return distance_to_move
    
    def time_to_move(self, key_list, vol_list, k_times):
        for k,  press_t in zip(key_list, k_times):
            # i = input("Enter to move to next key")
            print("Moving to key: {}".format(k))
            t = (((self.KEY_CONST*(k - self.previous_key)))/(self.max_freq*self.theta_m*self.radius))
            # print(t)
            if t<0:
                # print("Moving left")
                GPIO.output(self.direction, GPIO.HIGH) 
            elif t>0:
                # print("Moving right")
                GPIO.output(self.direction,GPIO.LOW)
            t = np.abs(t)
            # self.volume_adjust(v)
            # if t<=0.15:
            #     print("Short move")
            if k >= 0:
                PWM.start(self.pwm_pin,50, self.max_freq)
                time.sleep(t)
                PWM.stop(self.pwm_pin)
                self.previous_key = k
                self.press_key(press_t)
            else:
                # time.sleep(t)
                self.previous_key = self.previous_key
            # elif t>0.15:
            #     print("Long move")
            #     if k >= 0:
            #         PWM.start(self.pwm_pin,50, self.freq_curve[0])
            #         for f in self.freq_curve[1:]:
            #             PWM.set_frequency(self.pwm_pin,f)
            #             time.sleep(0.01)
                    
            #         time.sleep(t-0.065)
                    
            #         for f in reversed(self.freq_curve[1:]):
            #             PWM.set_frequency(self.pwm_pin,f)
            #             time.sleep(0.01)
            #         PWM.stop(self.pwm_pin)
            #         self.previous_key = k
            #         self.press_key(press_t)
            #     else:
            #         # time.sleep(t)
            #         self.previous_key = self.previous_key
        
            
            
# def main():
#     g = Gantry()
#     with open("key_list.csv",'r') as kfile:
#         key_list = np.genfromtxt(kfile)
#     with open("time_list.csv", 'r') as tfile:
#         key_times = np.genfromtxt(tfile)
#     with open("vol_list.csv",'r') as vfile:
#         vol = np.genfromtxt(vfile)

#     g.time_to_move(key_list, vol, key_times)
    
# if __name__ == "__main__":
#     main()
#     PWM.cleanup()
               
        
             