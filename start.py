import os 
from subprocess import *

p0 = Popen(["python3","detectSoundESP.py"],cwd=os.getcwd())

p1 = Popen(["python3","detectSoundPi.py"],cwd=os.getcwd())

p2 = Popen(["python3","web.py"],cwd=os.getcwd())

p2.wait()