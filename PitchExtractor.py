import pyaudio
import numpy as np
import time

out_time = []
out_key_list = []
out_vol_list = []
curr_key_i = 0
next_key_i = 1
curr_key_time = 0.0

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

def key_time(keys_arr, vols_arr):
    global out_time, keys_out, curr_key_i, curr_key_time, next_key_i, out_key, out_key_list, out_vol_list
    curr_key_i = 0
    next_key_i = 1
    if keys_arr[curr_key_i] == keys_arr[next_key_i]:
        out_key = keys_arr[curr_key_i]
        curr_key_time =+ 0.0625*2
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
                    
def create_audio_stream(FORMAT = pyaudio.paInt16, CHANNELS = 1, SAMPLE_RATE = 44100, WINDOW_SAMPLES = 2048, WINDOWS_PER_BUFFER = 5):
    FRAMES_PER_BUFFER =  WINDOW_SAMPLES * WINDOWS_PER_BUFFER
    FRAME_DIVIDER = 4
    KEY_FRAME_LEN = 256
    TIME_PER_KEY = (FRAMES_PER_BUFFER/FRAME_DIVIDER)/SAMPLE_RATE
    audio_obj = pyaudio.PyAudio()
    stream = audio_obj.open(
                    format = FORMAT,
                    channels = CHANNELS,
                    rate = SAMPLE_RATE,
                    input = True,
                    output = False,
                    frames_per_buffer = FRAMES_PER_BUFFER
                    )
    return stream
    
