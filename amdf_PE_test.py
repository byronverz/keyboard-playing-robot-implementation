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
        inputWindow_block = inputWindow[c*2560:(c*2560)+128]    
        for i,t in enumerate(tau):
            shifted = np.zeros_like(inputWindow_block)
            shifted[t:] = inputWindow_block[:-t]
            D_tau[c,i] = np.sum(np.abs(inputWindow_block-shifted))/128
            
        offset = np.argmax(D_tau[c])
        minIndices[c] = (c*128+offset)+np.argmin(D_tau[c,offset:-1])
        freq[c] = 44100/(minIndices[c]-(c*128))
        vol[c] = 20*np.log10(np.mean(np.abs(inputWindow))) - 96.3
    
    return freq, vol

def stft(inputWindow):
    fft = np.empty((4,1025))
    freq_out = np.empty(4)
    freqs = np.empty((4,1025))
    m = np.empty((4,1025))
    P = []
    for i in range(4):
        inputFrame = inputWindow[i*2560:(i*2560)+2048]
        fft[i] = 20*np.log10((np.abs(np.fft.rfft(inputFrame)))/len(inputFrame))
        freqs[i] = np.fft.rfftfreq(len(inputFrame),d =1./44100)
        for q, f in enumerate(fft[i]):
            if f>25:
                m[i,q] = np.abs(np.sign(f-fft[i,q-1])-np.sign(fft[i,q-1]-fft[i,q-2]))
            if m[i,q] == 2:
#                 print(i,q,fft[i,q])
#                 p_temp = 
                P.append(fft[i,q]*fft[i,q])
        freq_out[i] = freqs[i][np.argmax(fft[i])]
    
    return fft, freq_out,freqs
    
    
    
def freq_to_key(freq_arr):
    keys = np.zeros_like(freq_arr)
    keys = np.rint(12*np.log2(freq_arr/440)-2)
    # keys[keys<0] = -1
    return keys

def period_to_key(period_arr):
    keys = np.zeros_like(period_arr)
    keys = np.rint(2-12*np.log2(440*period_arr))
    return keys
    
def key_time(keys_arr, vols_arr):
    global out_time, keys_out, curr_key_i, curr_key_time, next_key_i, out_key, out_key_list, out_vol_list
    curr_key_i = 0
    next_key_i = 1
    if keys_arr[curr_key_i] == keys_arr[next_key_i]:
        out_key = keys_arr[curr_key_i]
        curr_key_time += 0.0625*2
        curr_key_i = next_key_i 
        next_key_i += 1
        
        try:
            key_time(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
        except IndexError:
            
            out_key_list.append(out_key)
            out_vol_list.append(vols_arr[curr_key_i])
            out_time.append(curr_key_time)
    else:
        if keys_arr[curr_key_i] == keys_arr[next_key_i+1]:
            
            out_key = keys_arr[curr_key_i]
            curr_key_time += 0.0625*3
            curr_key_i = next_key_i+1
            next_key_i += ((next_key_i+1)+1)
            
            try:
                key_time(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
            except IndexError:
                
                out_key_list.append(out_key)
                out_vol_list.append(vols_arr[curr_key_i])
                out_time.append(curr_key_time)
        else:
            if curr_key_time !=0:
                
                out_key_list.append(out_key)
                out_time.append(curr_key_time)
                out_vol_list.append(vols_arr[curr_key_i])
                curr_key_time = 0.0
                curr_key_i = next_key_i
                next_key_i += 1
                
                try:
                    key_time(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
                except IndexError:
                    
                    out_key_list.append(out_key)
                    out_vol_list.append(vols_arr[curr_key_i])
                    out_time.append(curr_key_time)
            else:
                curr_key_i = next_key_i
                next_key_i += 1
                try:
                     key_time(keys_arr[curr_key_i:], vols_arr[curr_key_i:])
                except IndexError:
                    
                    out_key_list.append(out_key)
                    out_vol_list.append(vols_arr[curr_key_i])
                    out_time.append(curr_key_time)
    
    
    
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
WINDOW_SAMPLES = 2048
WINDOWS_PER_BUFFER = 5
# FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
FRAMES_PER_BUFFER = 10240
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


# freqs_arr = np.empty((12,FRAME_DIVIDER))
# vols_arr = np.empty((12,FRAME_DIVIDER))
# period_array = np.empty((12, FRAME_DIVIDER))

for num_frames in range(12):   
    data = streamIn.read(FRAMES_PER_BUFFER)
    data_int = np.frombuffer(data, dtype = '<i2')
    # freqs_arr[num_frames], vols_arr[num_frames] = amdf_PE(data_int)
    s = time.time()
    spec, freqs, frange = stft(data_int)
    print(time.time()-s)
    

streamIn.stop_stream()
streamIn.close()
audio_obj.terminate()
    
# vols_arr = vols_arr.flatten()
# vols_arr = np.abs(vols_arr)
# vols_arr /= np.max(vols_arr)
# freqs_arr = freqs_arr.flatten()
# out_freq_list = freqs_arr.tolist()
# # out_period_list = period_array.flatten().tolist()
# key_array = freq_to_key(freqs_arr)
# key_arr = period_to_key(period_array)

# print("Number of {} frames recorded: {}".format(FRAMES_PER_BUFFER,len(freqs_arr)/8))
# print("Frequency array of length {}: \n{}".format(len(freqs_arr),freqs_arr.tolist()))
# print("Volume array: \n {}".format(vols_arr))
# print("Key number array of length {}: {} \n".format(len(key_array),key_array.tolist()))

# out_time = []
# out_key_list = []
# out_vol_list = []
# curr_key_i = 0
# next_key_i = 1
# curr_key_time = 0.0
# key_time(key_array,vols_arr)

# key_out = np.empty(int(len(key_array)/4))
# for k in range(0, int(len(key_array)/4)):
    # print(k, key_array[k*4:(k*4)+4])
    # key_out[k] = stats.mode(key_array[k*4:(k*4)+4], axis= None)[0][0]

# print("Out_key_list: {} \t out_time: {}".format(out_key_list, out_time))
# print("Out_vol_list: {}".format(out_vol_list))

# with open('data_file.csv','w') as data_file:
    # np.savetxt(data_file, data_in, fmt = '%10.3f', delimiter=',')
# with open('D_tau_file.csv','w') as d_tau_file:
    # np.savetxt(d_tau_file,D_tau, fmt = '%10.3f', delimiter = ',')
# with open("freq_list.csv", 'w') as freq_file:
    # np.savetxt(freq_file, freqs_arr, fmt = '%10,3f', delimiter = ',')
# with open('key_list.csv','w') as key_file:
#     np.savetxt(key_file, out_key_list, fmt = '%10.3f', delimiter = ',')
    
# with open('vol_list.csv','w') as vol_file:
#     np.savetxt(vol_file, out_vol_list, fmt = '%10.3f', delimiter = ',')
    
# with open('time_list.csv', 'w') as time_file:
#     np.savetxt(time_file, out_time, fmt = '%10.3f', delimiter = ',')

# with open('out_freq_list.csv','a') as of_file:
#     for item in out_freq_list:
#         of_file.write("%s \n" % item)

# with open('out_period_list.csv','a') as op_file:
#     for item in out_period_list:
#         op_file.write("%s \n" % item)        