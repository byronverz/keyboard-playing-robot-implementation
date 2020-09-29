import pyaudio
import numpy as np
import time


def amdf_PE(inputWindow):
    D_tau = np.zeros((FRAME_DIVIDER,KEY_FRAME_LEN))
    minIndices = np.zeros(FRAME_DIVIDER)
    freq = np.zeros(FRAME_DIVIDER)  
    vol = np.zeros(FRAME_DIVIDER)
    
    for c in range(FRAME_DIVIDER):
        inputWindow_block = inputWindow[c*KEY_FRAME_LEN:(c+1)*KEY_FRAME_LEN]
        tau = np.arange(1,(len(inputWindow_block)-1))
        shifted = np.zeros_like(inputWindow_block)
        shifted = inputWindow_block.copy()
        for i,t in enumerate(tau):
            temp = 0
            
            # if t == 0:
                # shifted = inputWindow_block
            # else:
                # shifted[:t] = 0
                # shifted[t:] = inputWindow_block[:-t]
    
            diffArr = np.abs(np.subtract(inputWindow_block,shifted))
            temp = (np.sum(diffArr)/len(inputWindow_block))
            D_tau[c,i] = temp
            shifted[:t] = 0
            shifted[t:] = inputWindow_block[:-t]
            
        offset = np.argmax(D_tau[c,:])
        minIndices[c] = (c*KEY_FRAME_LEN+offset)+np.argmin(D_tau[c,offset:-1])
        freq[c] = SAMPLE_RATE/(minIndices[c]-(c*KEY_FRAME_LEN))
#         vol[c] = (np.mean(np.abs(inputWindow_block))/2**15)
        vol[c] = 20*np.log10(np.mean(np.abs(inputWindow))) - 96.3
    
    return freq, vol

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
WINDOW_SAMPLES = 4096
WINDOWS_PER_BUFFER = 4
FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
FRAME_DIVIDER = 8
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

num_frames = 0
freqs_arr = []
vols_arr = []
timeEnd = 0
print("Start whistling!")
timeStart = time.time()

while num_frames <8:   
    data = streamIn.read(FRAMES_PER_BUFFER)
    # timeEnd = time.time()
    data_int = np.frombuffer(data, dtype = '<i2')
    frequency_array, volume_array = amdf_PE(data_int)
    freqs_arr.append(frequency_array)
    vols_arr.append(volume_array)
    num_frames += 1
    

vols_arr = np.array(vols_arr).flatten()
vols_arr /= np.max(vols_arr)
freqs_arr = np.array(freqs_arr).flatten()
print("Recording done \n Recording length: {}".format(timeEnd-timeStart))
print("Number of {} frames recorded: {}".format(FRAMES_PER_BUFFER,num_frames))
print("Frequency array of length {}: \n{}".format(len(freqs_arr),freqs_arr))
print("Volume array: \n {}".format(vols_arr))
keys = np.zeros_like(freqs_arr)
keys = np.rint(12*np.log2(freqs_arr/440)+36) # 36 must be changed to actual key number offset
vol_angles = 180*vols_arr
time_arr = np.array([TIME_PER_KEY for x in vol_angles])
print("Key number array: {}".format(keys))
print("Volume angle array: {}".format(vol_angles))

with open('key_list.csv','w') as key_file:
    np.savetxt(key_file, keys, fmt = '%10.3f', delimiter = ',')
    
with open('vol_list.csv','w') as vol_file:
    np.savetxt(vol_file, vol_angles, fmt = '%10.3f', delimiter = ',')
    
with open('time_list.csv', 'w') as time_file:
    np.savetxt(time_file, time_arr, fmt = '%10.3f', delimiter = ',')