import PitchExtractor as PE
import Gantry as G
import Adafruit_BBIO.GPIO as GPIO
import numpy as np


CHANNELS = 1
SAMPLE_RATE = 44100
WINDOW_SAMPLES = 2048
WINDOWS_PER_BUFFER = 5
FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
FRAME_DIVIDER = 4

out_time = []
out_key_list = []
out_vol_list = []
curr_key_i = 0
next_key_i = 1
curr_key_time = 0.0

whistle_pin = "P8_15"
GPIO.setup(whistle_pin, GPIO.OUT)

def main():
    # Define gantry object and home gantry
    g = G.Gantry()
    
    # Create audio stream and input arrays
    streamIn = PE.create_audio_stream()
    freqs_arr = np.empty((12,FRAME_DIVIDER))
    vols_arr = np.empty((12,FRAME_DIVIDER))
    
    # Start listening
    GPIO.output(whistle_pin, GPIO.HIGH)
    for num_frames in range(12):   
        data = streamIn.read(FRAMES_PER_BUFFER)
        data_int = np.frombuffer(data, dtype = '<i2')
        freqs_arr[num_frames], vols_arr[num_frames] = PE.amdf_PE(data_int)
    GPIO.output(whistle_pin,GPIO.LOW)
    
    # Process output arrays
    vols_arr /= np.max(np.abs(vols_arr.flatten()))
    freqs_arr = freqs_arr.flatten()
    
    # Convert frequencies to keys
    key_array = PE.freq_to_key(freqs_arr)
    # Get timing per key
    PE.key_time(key_array,vols_arr)
    
    # Start playing movement
    g.time_to_move(out_key_list, out_vol_list, out_time)
    
if __name__ == "__main__":
    main()