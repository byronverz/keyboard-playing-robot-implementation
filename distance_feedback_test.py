import qwiic_vl53l1x
import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

FREQUENCY = 1000

# Stepper pin setup
DIR_PIN = 'P8_8'
EN_PIN = 'P8_7'
pwm_pin = 'P8_13'

GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.output(EN_PIN,GPIO.LOW)
GPIO.output(DIR_PIN,GPIO.HIGH)

# ToF sensor setup
mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = 0x29)
mySensor.set_distance_mode(1)
if (mySensor.sensor_init() == None):
    print("Sensor online")

pwm.start(pwm_pin,50,FREQUENCY)
while True:
    mySensor.start_ranging()
    time.sleep(.005)
    distance = mySensor.get_distance()
    time.sleep(.005)
    mySensor.stop_ranging()
    PWM.set_frequency(pwm_pin,(distance*10))
    
