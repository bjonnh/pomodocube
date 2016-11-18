import hid
import time
import random
import math
import pyaudio
import sys
import os
import numpy as np
from select import select
import threading
from zmq.eventloop.ioloop import IOLoop

import zmq


def rotary():
    while True:
        for i in range(0,8):
            color = [random.randint(0,50),
                     random.randint(0,50),
                     random.randint(0,50)]
            color = [20, 0, 50]
            device.write([0x02]+color + [i]+ [ 0, 0 ,0]);
            
            for j in range(0,8):
                if j != i:
                    device.write([0x02]+[0,0,0] + [j] + [ 0, 0 ,0]);
            time.sleep(0.1);


def rotary_blend():
    while True:
        
        for i in range(0,8):
            color = [random.randint(0,50),
                     random.randint(0,50),
                     random.randint(0,50)]
            color = [20, 0, 50]
            device.write([0x02]+color + [i]+ [ 0, 0 ,0]);
            
            for j in range(0,8):
                if j != i:
                    d = 10.0*((i-j)%8 ) +1
                    color_fade = [int(c/d) for c in color]

                    device.write([0x02]+ color_fade + [j] + [ 0, 0 ,0]);
            time.sleep(0.5);

def sine_blend():
    angle=0
    color = [random.randint(0,50),
             random.randint(0,50),
             random.randint(0,50)]

    while True:
        for i in range(0,8):
            color_fade = [int((1+math.sin(angle*((i+2)/7.0)))*c/2) for c in color]

            device.write([0x02]+ color_fade + [i] + [ 0, 0 ,0]);
            time.sleep(0.01);
        angle += math.pi/40

def rand_color(scale=50):
    return [random.randint(0,scale%256),
             random.randint(0,scale%256),
             random.randint(0,scale%256)]
        
def sine_blend_glitch():
    angle=0
    color = [random.randint(0,50),
             random.randint(0,50),
             random.randint(0,50)]

    while True:
        if (random.random()>0.99):
            device.write([0x01]+ rand_color(255) + [0, 0, 0 ,0]);
            time.sleep(0.02)
            continue
        for i in range(0,8):
            color_fade = [int((1+math.sin(angle))*c/2) for c in color]

            device.write([0x02]+ color_fade + [i] + [ 0, 0 ,0]);
        time.sleep(0.001);
        angle += math.pi/400

def randomize_tint(color):
    return int(color + random.randint(-5,5))%50
        

def fire(brightness=50, force=255):
    angle=0
    color=[]
    color_fade=[]
    device.write([0xf0,brightness,0x00,0x00,0,0,0,0,0])
    little_force = int((force+1)/10)
    for led in range(0,8):
        basic_tint = random.randint(0,force)
        col = [basic_tint,
               random.randint(0,little_force),
               0]
        color.append(col)
        color_fade.append(col)
    while True:
        if random.random()>0.9:
            force += 1
            force = force%255
            little_force = int((force+1)/5) %255
            for j in range(0,8):
                color[j] = [int(color[j][0] + random.randint(-int(force/5),int(force/5)))%force,
                            int(color[j][1] + random.randint(-int(force/10),int(force/10)))%little_force,
                            0
                ]
        for i in range(0,8):
            ri = i#int(350*(1+math.sin(angle/1)))%8
            old_fade = color_fade[ri]
            color_fade[i] = [int((1+math.sin(angle*((i**2+2)/7.0)))*c/2) for c in color[i]]
            color_fade[i] = [int((old_fade[0] + color_fade[i][0]/10)/1.1),
                             int((old_fade[1] + color_fade[i][1]/10)/1.1),
                             0]

            device.write([0x02]+ color_fade[i] + [ri] + [ 0, 0 ,0]);
            time.sleep(0.001);
        angle += (force/64)*math.pi/64#36


class SpectrumAnalyzer:
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 512
    START = 0
    N = 512

    wave_x = 0
    wave_y = 0
    spec_x = 0
    spec_y = 0
    data = []
    led = 0
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        device.write([0xf0,0xff,0x00,0x00,0,0,0,0,0])
        self.stream = self.pa.open(format = self.FORMAT,
            channels = self.CHANNELS, 
            rate = self.RATE, 
            input = True,
            output = False,
            frames_per_buffer = self.CHUNK)
        # Main loop
        self.loop()
    def loop(self):
        try:
            while True :
                self.data = self.audioinput()
                self.fft()
                self.graphplot()

        except KeyboardInterrupt:
            self.pa.close()

        print("End...")

    def audioinput(self):
        ret = self.stream.read(self.CHUNK)
        ret = np.fromstring(ret, np.float32)
        return ret

    def fft(self):
        self.wave_x = range(self.START, self.START + self.N)
        self.wave_y = self.data[self.START:self.START + self.N]
        self.spec_x = np.fft.fftfreq(self.N, d = 1.0 / self.RATE)  
        y = np.fft.fft(self.data[self.START:self.START + self.N])    
        self.spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
    def graphplot(self):
        self.led += 1
        self.led = self.led%8
        bass = int(np.sum(self.spec_y[0:170])/17)
        medium = int(np.sum(self.spec_y[170:340])/2)
        treble = int(np.sum(self.spec_y[340:512])/17)
        print("{:03} {:03} {:03}".format(bass,medium,treble))
        device.write([0x02,bass%255,medium%255,treble%255,
                      self.led,0,0,0])


class NorthernLights:
    def __init__(self, device):
        self.brightness = 50
        self.speed = 1/18.0
        self.angle = 0
        self.color = []
        self.color_fade = []
        self.device = device

        for led in range(0, 8):
            basic_tint = random.randint(0, self.brightness)
            col = [basic_tint,
                   randomize_tint(basic_tint),
                   randomize_tint(basic_tint)]
            self.color.append(col)
            self.color_fade.append(col)

    def modify_colors(self):
        for j in range(0, 8):
            self.color[j] = [int(c + random.randint(-5, 5)) %
                             self.brightness for c in self.color[j]]

    def loop(self):
        if random.random() > 0.99:
            self.modify_colors()

        for i in range(0, 8):
            ri = i
            old_fade = self.color_fade[ri]
            self.color_fade[i] = [int((1+math.sin(self.angle*((i+2)/7.0)))*c/2)
                                  for c in self.color[i]]
            self.color_fade[i] = [
                int((old_fade[k] + self.color_fade[i][k]/10) / 1.1)
                for k in range(0, 3)]
            device.set_led_color_to(*self.color_fade[i], ri)

        self.angle += math.pi * self.speed

    def excite(self):
        self.speed = min(1/9.0, self.speed * 1.10)
        self.brightness = min(self.brightness+11, 255)
        self.modify_colors()
        print("Speed: {} - Brightness: {}".format(self.speed, self.brightness))

    def calm(self):
        self.speed = max(1/64, self.speed / 1.10)
        self.brightness = max(self.brightness-11, 50)
        self.modify_colors()
        print("Speed: {} - Brightness: {}".format(self.speed, self.brightness))


class Alarm:
    def __init__(self, device):
        self.brightness = 255
        self.angle = 0
        self.color = []
        self.color_fade = []
        self.device = device

        for led in range(0, 8):
            col = [255,
                   64,
                   0]
            self.color.append(col)
            self.color_fade.append(col)

    def loop(self):
        for i in range(0, 8):
            ri = i
            old_fade = self.color_fade[ri]
            self.color_fade[i] = [int((1+math.sin(self.angle*((i+2)/7.0)))*c/2)
                                  for c in self.color[i]]
            self.color_fade[i] = [
                int((old_fade[k] + self.color_fade[i][k]/10) / 1.1)
                for k in range(0, 3)]
            device.set_led_color_to(*self.color_fade[i], ri)

        self.angle += math.pi/18


class Device:
    TRIES = 3
    COLOR_PRESETS = 8

    def __init__(self, leds=8):
        tries = self.TRIES
        self.leds = leds

        while tries > 0:
            try:
                self.device = hid.device()
                self.device.open(0x16c0, 0x05df)
                break
            except OSError:
                time.sleep(0.5)
                self.tries -= 1
                if self.tries == 0:
                    print("Sorry couldn't connect")
                    sys.exit()
                pass

    def set_to_black(self):
        self.device.write([0x0])

    def set_colors_to(self, r, g, b):
        self.device.write([0x01, r % 256, g % 256, b % 256])

    def set_led_color_to(self, r, g, b, led):
        self.device.write([0x02, r % 256, g % 256, b % 256, led % self.leds])

    def set_colors_to_preset(self, color_preset):
        self.device.write([0x03, color_preset % self.COLOR_PRESETS])

    def set_led_color_to_preset(self, color_preset, led):
        self.device.write([0x04, color_preset % self.COLOR_PRESETS,
                           led % self.leds])

    def set_brightness(self, brightness):
        self.device.write([0xf0, brightness % 256])


class EventLoop:

    def __init__(self, device):
        self.device = device
        self.northern_lights = NorthernLights(self.device)
        self.alarm = Alarm(self.device)
        self.mode = "northern_lights"
        self.resettime = None
        self.commands = []

    def runcommand(self, command):
        if str(command) == 'alarm':
            print("Alarm mode")
            self.resettime = time.time()+5
            self.mode = "alarm"
        if str(command) == 'excite':
            self.northern_lights.excite()
        if str(command) == 'excited':
            for i in range(0, 25):
                self.northern_lights.excite()
        if str(command) == 'calm':
            self.northern_lights.calm()
        if str(command) == 'calmed':
            for i in range(0, 25):
                self.northern_lights.calm()
        if str(command) == 'high':
            self.device.set_brightness(255)
        if str(command) == 'medium':
            self.device.set_brightness(127)
        if str(command) == 'low':
            self.device.set_brightness(50)

    def loop(self):
        if self.resettime and time.time() > self.resettime:
            print("Normal mode")
            self.mode = "northern_lights"
            self.resettime = None

        if self.mode == "northern_lights":
            self.northern_lights.loop()
        if self.mode == "alarm":
            self.alarm.loop()

        time.sleep(0.05)


device = Device()
eventloop = EventLoop(device)


class LedWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            eventloop.loop()


class MessageWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:5555")
        while True:
            msg = socket.recv(copy=False)
            socket.send(msg)
            eventloop.runcommand(msg)

lw = LedWorker()
mw = MessageWorker()
lw.start()
mw.start()

