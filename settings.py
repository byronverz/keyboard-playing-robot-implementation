import numpy as np

def init():
    global out_key_list, out_vol_list, out_time, curr_key_time, next_key_i, curr_key_i, out_key
    out_time = []
    out_key_list = []
    out_vol_list = []
    curr_key_i = 0
    next_key_i = 1
    curr_key_time = 0.0
    out_key = 0