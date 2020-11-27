import PitchExtractor as PE
import Gantry as G
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import numpy as np


def cadence_controller(keys_arr, vols_arr):
    global out_time, out_vol,  keys_out, curr_key_i, curr_key_time, next_key_i, out_key, out_key_list, out_vol_list
    curr_key_i = 0
    next_key_i = 1
    if keys_arr[curr_key_i] == keys_arr[next_key_i]:
        out_key = keys_arr[curr_key_i]
        if curr_key_time != 0:
            curr_key_time += 0.06
            out_vol += vols_arr[next_key_i]
        elif curr_key_time == 0:
            curr_key_time += 0.06*2
            out_vol = vols_arr[curr_key_i] + vols_arr[next_key_i]
        curr_key_i = next_key_i 
        next_key_i += 1
        
        try:
            cadence_controller(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
        except IndexError:
            
            out_key_list.append(out_key)
            out_vol_list.append((out_vol/(curr_key_time/0.06)))
            out_time.append(curr_key_time)
    else:
        if len(keys_arr)>2:
            if keys_arr[curr_key_i] == keys_arr[next_key_i+1]:
                out_key = keys_arr[curr_key_i]
                if curr_key_time !=0:
                    curr_key_time += 0.06*2
                    out_vol += vols_arr[next_key_i] + vols_arr[next_key_i+1]
                elif curr_key_time == 0:
                    curr_key_time += 0.06*3
                    out_vol = vols_arr[curr_key_i] + vols_arr[next_key_i] + vols_arr[next_key_i+1]
                curr_key_i = next_key_i+1
                next_key_i += ((next_key_i+1)+1)
                
                try:
                    cadence_controller(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
                except IndexError:
                    
                    out_key_list.append(out_key)
                    out_vol_list.append((out_vol/(curr_key_time/0.06)))
                    out_time.append(curr_key_time)
            else:
                if curr_key_time !=0:
                    
                    out_key_list.append(out_key)
                    out_time.append(curr_key_time)
                    out_vol_list.append((out_vol/(curr_key_time/0.06)))
                    curr_key_time = 0.0
                    curr_key_i = next_key_i
                    next_key_i += 1
                    
                    try:
                        cadence_controller(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
                    except IndexError:
                        
                        out_key_list.append(out_key)
                        out_vol_list.append((out_vol/(curr_key_time/0.06)))
                        out_time.append(curr_key_time)
                else:
                    out_key_list.append(-100)
                    out_time.append(0.06)
                    out_vol_list.append(0.001)
                    curr_key_i = next_key_i
                    next_key_i += 1
                    try:
                         cadence_controller(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
                    except IndexError:
                        
                        out_key_list.append(out_key)
                        out_vol_list.append((out_vol/(curr_key_time/0.06)))
                        out_time.append(curr_key_time)
        else:
            out_key_list.append(out_key)
            out_time.append(curr_key_time+0.06)
            out_vol_list.append((out_vol/((curr_key_time+0.06)/0.06)))



def main():
    global out_key_list, out_vol_list, out_time
    whistle_pin = "P8_15"
    GPIO.setup(whistle_pin, GPIO.OUT)
    
    window_samples = 2048
    windows_per_buffer = 5
    frame_per_buffer =  window_samples * windows_per_buffer
    frame_divider = 4

    # Define gantry object and home gantry
    g = G.Gantry()
    
    w = input("Start recording?")
    if w == 'x':
        return
    # Create audio stream and input arrays
    streamIn = PE.create_audio_stream(WINDOW_SAMPLES = window_samples, WINDOWS_PER_BUFFER = windows_per_buffer)
    freqs_arr = np.empty((12,frame_divider))
    vols_arr = np.empty((12,frame_divider))
    
    # Start listening

    GPIO.output(whistle_pin, GPIO.HIGH)
    for num_frames in range(12):   
        data = streamIn.read(frame_per_buffer)
        data_int = np.frombuffer(data, dtype = '<i2')
        freqs_arr[num_frames], vols_arr[num_frames] = PE.amdf_PE(data_int)
    GPIO.output(whistle_pin,GPIO.LOW)
    streamIn.stop_stream()
    streamIn.close()
    
    # io = input("Audio processing done, move to playing?")
    # if io == 'x':
        # return
    # Process output arrays
    vols_arr = np.abs(vols_arr.flatten())
    vols_arr /= np.max(vols_arr)
    freqs_arr = freqs_arr.flatten()
    # print("Volume array: {}".format(vols_arr))
    # Convert frequencies to keys
    key_array = PE.freq_to_key(freqs_arr)
    print("Key array: {}".format(key_array.tolist()))
    # Get timing per key
    cadence_controller(key_array,vols_arr)
    # print("Out_key_list length: {} \t Out_vol_list length: {}".format(len(out_key_list), len(out_vol_list)))
    print("Out_key_list: {} \n Out_vol_list: {} \n Time list: {} \n Total time: {}".format(out_key_list, out_vol_list,out_time, np.sum(out_time)))
    for k,v in zip(out_key_list,out_vol_list):
        if k>0.0:
            print("Key : {} \t Volume : {}".format(k,v))
    # Start playing movement
    # out_key_list = [24,10,5,15,0,5]
    # out_vol_list = [0.9,0.5,0.9,0.5,0.9,0.25]
    # out_time = [0.5,0.25,0.25,0.25,0.5,0.325]
    # d_to_move = g.distance_to_move_calc(out_key_list)
    # input("Play audio")
    g.time_to_move(out_key_list, out_vol_list, out_time)
    # dist = []
    # freq = []
    # err = []
    # for k,t in zip(d_to_move, out_time):
    #     d,f,e = g.step_function(k,t)
    #     dist.append(d)
    #     freq.append(f)
    #     err.append(e)
    
    # print(dist)
    # print(freq)
    # print(err)
    
if __name__ == "__main__":
    
    out_time = []
    out_key_list = []
    out_vol_list = []
    curr_key_i = 0
    next_key_i = 1
    curr_key_time = 0.0
    curr_cadence_controller = 0.0
    
    main()
    PWM.cleanup()