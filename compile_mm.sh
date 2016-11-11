

echo "Pomodoro o"
avr-gcc -Os -Wall -o pomodocube.o -Ilibs-device -I. -mmcu=attiny85 -DF_CPU=16500000  -c pomodocube.c -Iusbdrv
echo "Light"
avr-gcc -Os -Wall -o light_ws2812.o -Ilibs-device -I. -mmcu=attiny85 -DF_CPU=16500000  -c light_ws2812.c -Iusbdrv
echo "Usbdrv"
avr-gcc -Os -DDEBUG_LEVEL=0  -o usbdrv/usbdrv.o -Iusbdrv -Ilibs-device -I. -mmcu=attiny85 -DF_CPU=16500000  -c usbdrv/usbdrv.c
avr-gcc -Os -DDEBUG_LEVEL=0  -o usbdrv/oddebug.o -Iusbdrv -Ilibs-device -I. -mmcu=attiny85 -DF_CPU=16500000  -c usbdrv/oddebug.c
avr-gcc -Os -DDEBUG_LEVEL=0  -o libs-device/osccal.o -Iusbdrv -Ilibs-device -I. -mmcu=attiny85 -DF_CPU=16500000  -c libs-device/osccal.c
echo "Usbdrvasm"
avr-gcc -Os -Wall -x assembler-with-cpp -o usbdrv/usbdrvasm.o -Ilibs-device -I. -mmcu=attiny85 -DF_CPU=16500000  -c usbdrv/usbdrvasm.S
echo "Full"
avr-gcc -Os -Wall -o pomodocube.elf -I. -mmcu=attiny85 -DF_CPU=16500000  pomodocube.o usbdrv/usbdrvasm.o usbdrv/oddebug.o usbdrv/usbdrv.o light_ws2812.o #libs-device/osccal.o 

avr-size pomodocube.elf
avr-objcopy -j .text  -j .data -O ihex pomodocube.elf pomodocube.hex
