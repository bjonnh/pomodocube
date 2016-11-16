import hid
import sys

while True:
    try:
        device = hid.device()
        device.open(0x16c0, 0x05df)
        break
    except OSError:
        pass

if len(sys.argv) != 9:
    print("Not enough arguments")
else:
    device.write([int(arg,16) for arg in sys.argv[1:]])
