# import Adafruit_GPIO.I2C as I2C
import qwiic_vl53l1x
import time

# device = I2C.Device(0x29,2)
# def_dev = I2C.get_i2c_device(I2C.get_default_bus())
# print(dir(def_dev._bus))
# # while True:
#     # byte = i2c.readU8

mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = 0x29)
mySensor.set_distance_mode(1)
print(mySensor.sensor_init())
if (mySensor.sensor_init() == None):
    print("Sensor online")

start = time.time()
timer = 0.0    
while timer<3.0:
    mySensor.start_ranging()
    time.sleep(.005)
    distance = mySensor.get_distance()
    time.sleep(.005)
    mySensor.stop_ranging()
    timer = time.time() - start
    
    print("Distance {}".format(distance))