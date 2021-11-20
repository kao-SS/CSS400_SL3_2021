import pyaudio
import socket
from numpy import record
import pyaudio
import math
import struct
import wave
import time
import os
import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import wavfile
import subprocess
import contextlib

Threshold = 305

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
TIMEOUT_LENGTH = 1
f_name_directory = r'records'

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

#f=open("demo", "ab")

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 4444

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        #print(type(frame))
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    # def __init__(self):
    #     self.p = pyaudio.PyAudio()
    #     self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=chunk)

    def record(self):
        global s
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            #data = self.stream.read(chunk, exception_on_overflow=False)
            data, addr = s.recvfrom(1500)
            
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH
            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):

        n_files = len(os.listdir(f_name_directory))
        filename = os.path.join(f_name_directory, '{}.wav'.format(n_files))

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        
        duration = 0
        with contextlib.closing(wave.open(filename, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)

        if duration>2.1:
            rate, rtemp = wavfile.read(filename)
            dtemp = butter_lowpass_filter(rtemp, 2000, rate)
            dtemp = dtemp-np.mean(dtemp)
            wavfile.write(filename,rate,np.int16(dtemp/np.max(np.abs(dtemp))*32767))
            
            print('Written to file: {}'.format(filename))

            subprocess.Popen(["python3", "googleS2T.py",filename, "esp"], cwd=os.getcwd())

        else:
            os.remove(filename)
            print("file too short deleting")

        print('Returning to listening')



    def listen(self):
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        print("server started")
        data, addr = s.recvfrom(1500)
        print('Listening beginning')
        while True:
            #input = self.stream.read(chunk, exception_on_overflow=False)
            input = data
            data, addr = s.recvfrom(1500)
            rms_val = self.rms(input)
            #print(rms_val)
            if rms_val > Threshold:
                self.record()

a = Recorder()
a.listen()


