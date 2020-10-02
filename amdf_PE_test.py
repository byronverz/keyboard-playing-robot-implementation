import pyaudio
import numpy as np
import time


def amdf_PE(inputWindow):
    D_tau = np.zeros((8,128))
    minIndices = np.empty(8)
    freq = np.empty(8)
    vol = np.empty(8)
    tau = np.arange(1,127)
    
    for c in range(8):       
        inputWindow_block = inputWindow[c*1280:(c*1280)+128]    
        for i,t in enumerate(tau, start = 1):
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
print(streamIn.get_input_latency())
# num_frames = 0
freqs_arr = np.empty((8,FRAME_DIVIDER))
vols_arr = np.empty((8,FRAME_DIVIDER))
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
for num_frames in range(8):   
    data = streamIn.read(FRAMES_PER_BUFFER)
    data_int = np.frombuffer(data, dtype = '<i2')
    # s = time.time()
    freqs_arr[num_frames], vols_arr[num_frames] = amdf_PE(data_int)
    # e = time.time()
    # times.append(e-s)
    # num_frames += 1
#     # print(num_frames)
# except:
# print(times)
    
# streamIn.stop_stream()
# streamIn.close()
# audio_obj.terminate()
    
# data_in = np.array(data_in).flatten()
# D_tau = np.array(D_tau).flatten()
vols_arr = vols_arr.flatten()
vols_arr /= np.max(vols_arr)
freqs_arr = freqs_arr.flatten()
# mins = np.array(mins).flatten()
# print("Recording done \t Recording length: {}".format(timeEnd-timeStart))
print("Number of {} frames recorded: {}".format(FRAMES_PER_BUFFER,num_frames))
print("Frequency array of length {}: \n{}".format(len(freqs_arr),freqs_arr))
# print("Minimum index array: \n {}".format(mins))
print("Volume array: \n {}".format(vols_arr))
keys = np.zeros_like(freqs_arr)
keys = np.rint(12*np.log2(freqs_arr/440)+49) # 36 must be changed to actual key number offset
# vol_angles = 180*vols_arr
# time_arr = np.array([TIME_PER_KEY for x in vol_angles])
print("Key number array: {}".format(keys))
# # print("Volume angle array: {}".format(vol_angles))


# with open('data_file.csv','w') as data_file:
    # np.savetxt(data_file, data_in, fmt = '%10.3f', delimiter=',')
# with open('D_tau_file.csv','w') as d_tau_file:
    # np.savetxt(d_tau_file,D_tau, fmt = '%10.3f', delimiter = ',')
# with open('key_list.csv','w') as key_file:
#     np.savetxt(key_file, keys, fmt = '%10.3f', delimiter = ',')
    
# with open('vol_list.csv','w') as vol_file:
#     np.savetxt(vol_file, vol_angles, fmt = '%10.3f', delimiter = ',')
    
# with open('time_list.csv', 'w') as time_file:
#     np.savetxt(time_file, time_arr, fmt = '%10.3f', delimiter = ',')