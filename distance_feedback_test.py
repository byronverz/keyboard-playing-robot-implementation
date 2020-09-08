import qwiic_vl53l1x
import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import sys

FREQUENCY = 1000

# Stepper pin setup
DIR_PIN = 'P8_8'
EN_PIN = 'P8_7'
MOTOR_PWM = 'P8_13'
SERVO_PWM = 'P9_16'

GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(EN_PIN, GPIO.OUT)
# GPIO.output(EN_PIN,GPIO.LOW)
# GPIO.output(DIR_PIN,GPIO.HIGH)

# ToF sensor setup
mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = 0x29)
init = mySensor.sensor_init()
# if init != 0:
    # print("Failed to initialize sensor")
    # sys.exit()
mySensor.set_distance_mode(1)
print(mySensor.sensor_init())
if (mySensor.sensor_init() == None):
    print("Sensor online")

# PWM.start(MOTOR_PWM,50,FREQUENCY)
# PWM.start(SERVO_PWM,50,120)
while True:
    mySensor.start_ranging()
    time.sleep(.005)
    distance = mySensor.get_distance()
    time.sleep(.005)
    mySensor.stop_ranging()
    # PWM.set_frequency(MOTOR_PWM,(distance*10))
    # PWM.set_duty_cycle(SERVO_PWM, (distance/10))
    print("Distance: {} mm".format(distance))
