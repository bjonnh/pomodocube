import hid
import time
import random
import math
import pyaudio
import numpy as np

while True:
    try:
        device = hid.device()
        device.open(0x16c0, 0x05df)
        break
    except OSError:
        pass

print("Opened")

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
        
def northern_lights(brightness=50):
    angle=0
    color=[]
    color_fade=[]
    device.write([0xf0,brightness,0x00,0x00,0,0,0,0,0])
    for led in range(0,8):
        basic_tint = random.randint(0,brightness)
        col = [basic_tint,
                      randomize_tint(basic_tint),
                      randomize_tint(basic_tint)]
        color.append(col)
        color_fade.append(col)
    while True:
        if random.random()>0.99:
            for j in range(0,8):
                color[j] = [int(c + random.randint(-5,5))%brightness for c in color[j]]
        for i in range(0,8):
            ri = i#int(350*(1+math.sin(angle/1)))%8
            old_fade = color_fade[ri]
            color_fade[i] = [int((1+math.sin(angle*((i+2)/7.0)))*c/2) for c in color[i]]
            color_fade[i] = [int((old_fade[k] + color_fade[i][k]/10)/1.1) for k in range(0,3)]

            device.write([0x02]+ color_fade[i] + [ri] + [ 0, 0 ,0]);
            time.sleep(0.001);
        angle += math.pi/18#36


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

def gradient_fire():
    bass=0
    medium=0
    treble=0
    starttime=time.time()
    while True:
        for i in range(0,8):
            device.write([0x02,bass,medium,treble,
                          i])
            if bass < 255:
                bass +=1
            elif medium < 255:
                medium += 1
            elif treble < 255:
                treble +=1
            else:
                bass = 0
                medium = 0
                treble = 0
                t = (time.time()-starttime)
                starttime = time.time()
                print("FPS: {}".format(3*255/t))
              #print()
#rotary_blend()        
#sine_blend()
#northern_lights(255)
fft=SpectrumAnalyzer()
#gradient_fire()
#fire(255, 32) fire is dirty and buggy don't use it

#device.write([0x04,0x01,0x01,0,0,0,0,0])

