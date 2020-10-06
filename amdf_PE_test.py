import pyaudio
import numpy as np
import time
from scipy import stats

def amdf_PE(inputWindow):
    D_tau = np.zeros((2,128))
    minIndices = np.empty(2)
    freq = np.empty(2)
    vol = np.empty(2)
    tau = np.arange(1,128)
    
    for c in range(2):       
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

FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
WINDOW_SAMPLES = 2048
WINDOWS_PER_BUFFER = 5
FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
FRAME_DIVIDER = 2
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
# num_frames = 0
freqs_arr = np.empty((12,FRAME_DIVIDER))
vols_arr = np.empty((12,FRAME_DIVIDER))
# times = []
# print("Start whistling!")
# data = streamIn.read(FRAMES_PER_BUFFER)
# data_int = np.frombuffer(data, dtype = '<i2')
# s = time.time()
# freqs_arr[0], vols_arr[0] = amdf_PE(data_int)
# e = time.time()
# print("AMDF Time taken: {}".format(e-s))
# print(freqs_arr)
# try:
for num_frames in range(12):   
    data = streamIn.read(FRAMES_PER_BUFFER)
    data_int = np.frombuffer(data, dtype = '<i2')
    freqs_arr[num_frames], vols_arr[num_frames] = amdf_PE(data_int)
    # print(num_frames)
    # time.sleep(0.1)

streamIn.stop_stream()
streamIn.close()
audio_obj.terminate()
    
# data_in = np.array(data_in).flatten()
# D_tau = np.array(D_tau).flatten()
vols_arr = vols_arr.flatten()
vols_arr /= np.max(vols_arr)
freqs_arr = freqs_arr.flatten()
# mins = np.array(mins).flatten()
# print("Recording done \t Recording length: {}".format(timeEnd-timeStart))
print("Number of {} frames recorded: {}".format(FRAMES_PER_BUFFER,len(freqs_arr)/8))
print("Frequency array of length {}: \n{}".format(len(freqs_arr),freqs_arr))
# print("Minimum index array: \n {}".format(mins))
print("Volume array: \n {}".format(vols_arr))
keys = np.zeros_like(freqs_arr)
keys = np.rint(12*np.log2(freqs_arr/440)+28) # 36 must be changed to actual key number offset
# vol_angles = 180*vols_arr

print("Key number array of length {}: {}".format(len(keys),keys))
key_out = np.empty(int(len(keys)/4))
# for i in range(8):
    # print(i)
for k in range(0, int(len(keys)/4)):
    print(k, keys[k*4:(k*4)+4])
    key_out[k] = stats.mode(keys[k*4:(k*4)+4], axis= None)[0][0]

print(key_out)
# with open('data_file.csv','w') as data_file:
    # np.savetxt(data_file, data_in, fmt = '%10.3f', delimiter=',')
# with open('D_tau_file.csv','w') as d_tau_file:
    # np.savetxt(d_tau_file,D_tau, fmt = '%10.3f', delimiter = ',')
with open('key_list.csv','w') as key_file:
    np.savetxt(key_file, key_out, fmt = '%10.3f', delimiter = ',')
    
# with open('vol_list.csv','w') as vol_file:
#     np.savetxt(vol_file, vol_angles, fmt = '%10.3f', delimiter = ',')
    
# with open('time_list.csv', 'w') as time_file:
#     np.savetxt(time_file, time_arr, fmt = '%10.3f', delimiter = ',')