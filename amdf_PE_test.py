import pyaudio
import numpy as np
import time
from scipy import stats

def amdf_PE(inputWindow):
    D_tau = np.zeros((4,128))
    minIndices = np.empty(4)
    freq = np.empty(4)
    vol = np.empty(4)
    tau = np.arange(1,128)
    
    for c in range(4):       
        inputWindow_block = inputWindow[c*1280:(c*1280)+128]    
        for i,t in enumerate(tau):
            shifted = np.zeros_like(inputWindow_block)
            shifted[t:] = inputWindow_block[:-t]
            D_tau[c,i] = np.sum(np.abs(inputWindow_block-shifted))/128
            
        offset = np.argmax(D_tau[c])
        minIndices[c] = (c*128+offset)+np.argmin(D_tau[c,offset:-1])
        freq[c] = (44100/(minIndices[c]-(c*128)))
        vol[c] = 20*np.log10(np.mean(np.abs(inputWindow))) - 96.3
    
    return freq, vol


def freq_to_key(freq_arr):
    keys = np.zeros_like(freq_arr)
    keys = np.rint(12*np.log2(freq_arr/440)-2)
    return keys

def key_time(keys_arr):
    global out_time, keys_out, curr_key_i, curr_key_time, next_key_i, out_key, out_key_list
    curr_key_i = 0
    next_key_i = 1
    if keys_arr[curr_key_i] == keys_arr[next_key_i]:
        out_key = keys_arr[curr_key_i]
        curr_key_time =+ 0.0625*2
        curr_key_i = next_key_i 
        next_key_i += 1
        # print("Case 1: Current and next equal \n curr_i: {} \t next_i: {}".format(curr_key_i,next_key_i))
        # print("1. New keys_arr: {}".format(keys_arr[curr_key_i:]))
        try:
            key_time(keys_arr[curr_key_i:])
        except IndexError:
            # print("End of key list")
            out_key_list.append(out_key)
            out_time.append(curr_key_time)
    else:
        if keys_arr[curr_key_i] == keys_arr[next_key_i+1]:
            
            out_key = keys_arr[curr_key_i]
            curr_key_time += 0.0625*3
            curr_key_i = next_key_i+1
            next_key_i += ((next_key_i+1)+1)
            # print("Case 2: Current and next + 1 equal \n curr_i: {} \t next_i: {}".format(curr_key_i,next_key_i))
            # print("2. New keys_arr: {}".format(keys_arr[curr_key_i:]))
            try:
                key_time(keys_arr[curr_key_i:])
            except IndexError:
                # print("End of key list")
                out_key_list.append(out_key)
                out_time.append(curr_key_time)
        else:
            if curr_key_time !=0:
                
                out_key_list.append(out_key)
                out_time.append(curr_key_time)
                curr_key_time = 0.0
                curr_key_i = next_key_i
                next_key_i += 1
                # print("Case 3: End time for key: {}".format(keys_arr[curr_key_i-1]))
                # print("3. New keys_arr: {}".format(keys_arr[curr_key_i:]))
                try:
                    key_time(keys_arr[curr_key_i:])
                except IndexError:
                    # print("End of key list")
                    out_key_list.append(out_key)
                    out_time.append(curr_key_time)
            else:
                curr_key_i = next_key_i
                next_key_i += 1
                try:
                     key_time(keys_arr[curr_key_i:])
                except IndexError:
                    # print("End of key list")
                    out_key_list.append(out_key)
                    out_time.append(curr_key_time)
    
    
    
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
WINDOW_SAMPLES = 2048
WINDOWS_PER_BUFFER = 5
FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
FRAME_DIVIDER = 4
KEY_FRAME_LEN = 256
TIME_PER_KEY = (FRAMES_PER_BUFFER/FRAME_DIVIDER)/SAMPLE_RATE

audio_obj = pyaudio.PyAudio()
streamIn = audio_obj.open(
                format = FORMAT,
                channels = CHANNELS,
                rate = SAMPLE_RATE,
                input = True,
                output = False,
                frames_per_buffer = FRAMES_PER_BUFFER
                )
print(streamIn.get_input_latency())

freqs_arr = np.empty((12,FRAME_DIVIDER))
vols_arr = np.empty((12,FRAME_DIVIDER))

for num_frames in range(12):   
    data = streamIn.read(FRAMES_PER_BUFFER)
    data_int = np.frombuffer(data, dtype = '<i2')
    freqs_arr[num_frames], vols_arr[num_frames] = amdf_PE(data_int)


streamIn.stop_stream()
streamIn.close()
audio_obj.terminate()
    
vols_arr = vols_arr.flatten()
# vols_arr /= np.max(np.abs(vols_arr))
freqs_arr = freqs_arr.flatten()
key_array = freq_to_key(freqs_arr)
print("Number of {} frames recorded: {}".format(FRAMES_PER_BUFFER,len(freqs_arr)/8))
print("Frequency array of length {}: \n{}".format(len(freqs_arr),freqs_arr.tolist()))
print("Volume array: \n {}".format(vols_arr))
print("Key number array of length {}: {} \n".format(len(key_array),key_array.tolist()))
out_time = []
out_key_list = []
curr_key_i = 0
next_key_i = 1
curr_key_time = 0.0
key_time(key_array)
# key_out = np.empty(int(len(key_array)/4))
# for k in range(0, int(len(key_array)/4)):
    # print(k, key_array[k*4:(k*4)+4])
    # key_out[k] = stats.mode(key_array[k*4:(k*4)+4], axis= None)[0][0]

print("Out_key_list: {} \t out_time: {}".format(out_key_list, out_time))

# with open('data_file.csv','w') as data_file:
    # np.savetxt(data_file, data_in, fmt = '%10.3f', delimiter=',')
# with open('D_tau_file.csv','w') as d_tau_file:
    # np.savetxt(d_tau_file,D_tau, fmt = '%10.3f', delimiter = ',')
# with open('key_list.csv','w') as key_file:
    # np.savetxt(key_file, key_out, fmt = '%10.3f', delimiter = ',')
    
# with open('vol_list.csv','w') as vol_file:
#     np.savetxt(vol_file, vol_angles, fmt = '%10.3f', delimiter = ',')
    
# with open('time_list.csv', 'w') as time_file:
#     np.savetxt(time_file, time_arr, fmt = '%10.3f', delimiter = ',')