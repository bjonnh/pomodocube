import hid
import time
import random
import math


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
            time.sleep(0.0001);
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

        
northern_lights(150)

#device.write([0x04,0x01,0x01,0,0,0,0,0])

