DEVICE = attiny85 # I don't promise it will work with anything else
F_CPU = 16500000
FLASH=./micronucleus

# If you don't use micronucleus
# FLASH=avrdude -c usbasp -p$(DEVICE)


OPTFLAGS = -Os -flto
INCLUDES =  -Iv-usb/libs-device -I. -Iv-usb/usbdrv -DDEBUG_LEVEL=0
CFLAGS = $(OPTFLAGS) -Wall $(INCLUDES) -mmcu=$(DEVICE) -DF_CPU=$(F_CPU)
OBJECTS = main.o light_ws2812.o v-usb/usbdrv/usbdrv.o v-usb/usbdrv/oddebug.o v-usb/libs-device/osccal.o  v-usb/usbdrv/usbdrvasm.o
COMPILE= avr-gcc $(CFLAGS)


.S.o:
	$(COMPILE) -x assembler-with-cpp -c $< -o $@

.c.o:
	$(COMPILE) -c $< -o $@

flash: hex
	$(FLASH) main.hex

main.elf: $(OBJECTS)
	$(COMPILE) $(OBJECTS) -o $@

main.hex: main.elf
	avr-objcopy -j .text -j .data -O ihex main.elf main.hex
	avr-size main.hex

hex: main.hex

clean:
	rm -f main.hex main.elf $(OBJECTS)

