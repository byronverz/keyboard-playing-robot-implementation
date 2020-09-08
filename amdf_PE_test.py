import pyaudio
import numpy as np
import time

def amdf_PE(inputWindow):
    D_tau = np.zeros((8,256))
    minIndices = np.zeros(8)
    freq = np.zeros(8)  
    vol = np.zeros(8)
    
    for c in range(8):
        inputWindow_block = inputWindow[c*256:(c+1)*256]
        tau = np.arange(0,(len(inputWindow_block)-1))
        for i,t in enumerate(tau):
            temp = 0
            shifted = np.zeros_like(inputWindow_block)
            if t == 0:
                shifted = inputWindow_block
            else:
                shifted[:t] = 0
                shifted[t:] = inputWindow_block[:-t]
    
            diffArr = np.abs(np.subtract(inputWindow_block,shifted))
            temp = (np.sum(diffArr)/len(inputWindow_block))
            D_tau[c,i] = temp
        offset = np.argmax(D_tau[c,:])
        minIndices[c] = (c*256+offset)+np.argmin(D_tau[c,offset:-1])
        freq[c] = SAMPLE_RATE/(minIndices[c]-(c*256))
#         vol[c] = (np.mean(np.abs(inputWindow_block))/2**15)
        vol[c] = 20*np.log10(np.mean(np.abs(inputWindow))) - 96.3
    
    return freq, vol

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
WINDOW_SAMPLES = 4096
WINDOWS_PER_BUFFER = 5
FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
TIME_PER_KEY = 0.058

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
timeStart = time.time()
timeEnd = 0
while (timeEnd-timeStart) < 3.0:   
    num_frames += 1
    data = streamIn.read(FRAMES_PER_BUFFER)
    data_int = np.frombuffer(data, dtype = '<i2')
    frequency_array, volume_array = amdf_PE(data_int)
    freqs_arr.append(frequency_array)
    vols_arr.append(volume_array)
    timeEnd = time.time()
    
vols_arr = np.array(vols_arr).flatten()
vols_arr /= np.max(vols_arr)
freqs_arr = np.array(freqs_arr).flatten()
print("Recording done")
print("Frequency array: \n{}".format(freqs_arr))
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