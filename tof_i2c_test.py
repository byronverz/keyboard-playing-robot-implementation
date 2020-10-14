# import Adafruit_GPIO.I2C as I2C
import qwiic_vl53l1x
import time

# device = I2C.Device(0x29,2)
# def_dev = I2C.get_i2c_device(I2C.get_default_bus())
# print(dir(def_dev._bus))
# # while True:
#     # byte = i2c.readU8

mySensor = qwiic_vl53l1x.QwiicVL53L1X(address = 0x29)
mySensor.sensor_init()
mySensor.set_distance_mode(1)
mySensor.set_roi(8,8)
mySensor.set_offset(23)
mySensor.set_inter_measurement_in_ms(200)
mySensor.set_timing_budget_in_ms(100)
print("Boot state: {}".format(mySensor.boot_state()))
print("Ambient per SPAD: {}".format(mySensor.get_ambient_per_spad()))
print("Ambient rate: {}".format(mySensor.get_ambient_rate()))
print("High distance threshold: {}".format(mySensor.get_distance_threshold_high()))
print("Low distance threshold: {}".format(mySensor.get_distance_threshold_low()))
print("Distance threshold window: {}".format(mySensor.get_distance_threshold_window()))
print("Intermeasurement period: {}".format(mySensor.get_inter_measurement_in_ms()))
print("Interrupt polarity: {}".format(mySensor.get_interrupt_polarity()))
print("Offset distance: {}".format(mySensor.get_offset()))
print("Range status: {}".format(mySensor.get_range_status()))
print("ROI XY: {}".format(mySensor.get_roi_xy()))
print("Sigma threshold: {}".format(mySensor.get_sigma_threshold()))
print("Signal per SPAD: {}".format(mySensor.get_signal_per_spad()))
print("Signal rate: {}".format(mySensor.get_signal_rate()))
print("Signal threshold: {}".format(mySensor.get_signal_threshold()))
print("Enabled SPADs: {}".format(mySensor.get_spad_nb()))
print("Timing budget: {}".format(mySensor.get_timing_budget_in_ms()))
print("Cross talk: {}".format(mySensor.get_xtalk()))

# mySensor.set_distance_mode(2)
# print(mySensor.sensor_init())
# if (mySensor.sensor_init() == None):
    # print("Sensor online")
# mySensor.set_roi(8,8)
# start = time.time()
# print(mySensor.get_ambient_per_spad())
# timer = 0.0
distances = []
for k in range(25):
    key_measures = []
    ready = input("Measuring distance for key {}: ".format(k))
    if ready == 'y':
        for n in range(10):
            mySensor.start_ranging()
            # time.sleep(.01)
            distance = mySensor.get_distance()
            # time.sleep(.01)
            mySensor.stop_ranging()
            distances.append(distance)
    key_measures.append(distances)
        
print(key_measures)
