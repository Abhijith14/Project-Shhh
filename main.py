import win32api
import win32gui
import sys
import trace
import threading
import time
import sounddevice as sd
import numpy as np
import playsound
import pygame
import keyboard

class thread_with_trace(threading.Thread):
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False
 
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run     
    threading.Thread.start(self)
 
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
 
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
 
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
 
  def kill(self):
    self.killed = True



WM_APPCOMMAND = 0x319

APPCOMMAND_MICROPHONE_VOLUME_UP = 0x1a
APPCOMMAND_MICROPHONE_VOLUME_DOWN = 0x19
APPCOMMAND_MICROPHONE_VOLUME_MUTE = 0x180000
test = []

def low_vol():
    win32api.SendMessage(-1, 0x319, 0x30292, APPCOMMAND_MICROPHONE_VOLUME_DOWN * 0x10000)

def high_vol():
    win32api.SendMessage(-1, 0x319, 0x30292, APPCOMMAND_MICROPHONE_VOLUME_UP * 0x10000)

def mute_vol():
    hwnd_active = win32gui.GetForegroundWindow()
    win32api.SendMessage(hwnd_active, WM_APPCOMMAND, None, APPCOMMAND_MICROPHONE_VOLUME_MUTE)

def print_sound(indata, outdata, frames, time, status):
    global test
    volume_norm = np.linalg.norm(indata)*10
    #print ("|" * int(volume_norm))
    #print(int(volume_norm))
    test.append(int(volume_norm))

def start_check():
    global test
    with sd.Stream(callback=print_sound):
        sd.sleep(1000)
    temp = False
    #print(test)
    for i in test:
        if i > 0:
            temp = True
    test.clear()
    return temp


def reduce_vol():
    t1 = thread_with_trace(target=low_vol)
    t2 = thread_with_trace(target=mute_vol)
    t1.start()

    print("Muted..")
    t1.kill()
    time.sleep(1)
    t2.start()


#def decrease_vol():
#    t1 = thread_with_trace(target=low_vol)
#    t1.start()
#    time.sleep(1)
#    print("Muted")
#    t1.kill()


def increase_vol():
    t1 = thread_with_trace(target=high_vol)
    t1.start()
    time.sleep(1)
    print("Unmuted")
    t1.kill()


def play_sound():
  #playsound.playsound('audio.mp3')
  pygame.mixer.init()
  pygame.mixer.music.load('audio.mp3')
  pygame.mixer.music.play()


def key_detect():
  if start_check():
    reduce_vol()
    play_sound()
  else:
    increase_vol()
    



if __name__ == "__main__":

    keyboard.add_hotkey('ctrl + shift + z', key_detect)
    keyboard.wait()

    #decrease_vol()
    print("DONE!!")
