/*
 *
 * This example is configured for a Atmega32 at 16MHz
 */ 

#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include "light_ws2812.h"
#include <avr/pgmspace.h>
#include "usbdrv.h"
#include "requests.h"
#include <avr/wdt.h>
#include "oddebug.h"
#include "osccal.h"
//#define sei() asm volatile("sei")
//#define cli() asm volatile("cli")
//#define nop() asm volatile("nop")

#define MAXPIX 8

struct cRGB led[MAXPIX];


uint8_t update=0;
#define BUFLEN 8
uchar param[BUFLEN];

#define UPDATEDELAY 64

static uchar    currentAddress;
static uchar    bytesRemaining;

// Commands
// 0 . . . . . . . : Reset to black
// 1 r g b . . . . : Set all to color r g b
// 2 r g b l . . . : Set led l to color r g b

void react(void) {
	uint8_t i;

	switch (param[0]) {
	case 0: // Set off all
		for(i=MAXPIX; i>0; i--)
		{    
			led[i-1].r=0;led[i-1].g=0;led[i-1].b=0;
		}
		
		update=UPDATEDELAY;

		break;
	case 1: // Full color
		for(i=MAXPIX; i>0; i--)
		{    
			led[i-1].r=param[1];led[i-1].g=param[2];led[i-1].b=param[3];
		}

		update=UPDATEDELAY;
		break;
	case 2: // Set
		led[param[4]%8].r=param[1];led[param[4]%8].g=param[2];led[param[4]%8].b=param[3];

		update=UPDATEDELAY;
		break;
	}

}

// Function
// 1: led on (single), params: r,g,b
void setup(void)
{
       
//	DDRB|=_BV(ws2812_pin);
		
	uint8_t i;
	for(i=MAXPIX; i>0; i--)
	{    
	    led[i-1].r=0;led[i-1].g=0;led[i-1].b=0;
	}
	update=255;
}


PROGMEM const char usbHidReportDescriptor[22] = {    /* USB report descriptor */
    0x06, 0x00, 0xff,              // USAGE_PAGE (Generic Desktop)
    0x09, 0x01,                    // USAGE (Vendor Usage 1)
    0xa1, 0x01,                    // COLLECTION (Application)
    0x15, 0x00,                    //   LOGICAL_MINIMUM (0)
    0x26, 0xff, 0x00,              //   LOGICAL_MAXIMUM (255)
    0x75, 0x08,                    //   REPORT_SIZE (8)
    0x95, 0x08,                    //   REPORT_COUNT (128)
    0x09, 0x00,                    //   USAGE (Undefined)
    0xb2, 0x02, 0x01,              //   FEATURE (Data,Var,Abs,Buf)
    0xc0                           // END_COLLECTION
};
uchar   usbFunctionRead(uchar *data, uchar len)
{
	if (len > bytesRemaining)
		len = bytesRemaining;
	for (int i=0; i<len; i++) {
		data[i] = param[i];
	}
	currentAddress += len;
	bytesRemaining -= len;
	return len;
}

uchar   usbFunctionWrite(uchar *data, uchar len)
{
	memcpy(param, data, len);
//	param[0] = data[0];
	react();
/*	for (i=0;i<len;i++) {
		if (bufpos<BUFLEN) {
			param[bufpos] = data[i];
			bufpos++;
		}
	}
	if (bufpos==BUFLEN) {
		react();
		bufpos=0;
	}
*/
	return 1;
}


usbMsgLen_t usbFunctionSetup(uchar data[8])
{
	usbRequest_t    *rq = (void *)data;

    if((rq->bmRequestType & USBRQ_TYPE_MASK) == USBRQ_TYPE_CLASS){    /* HID class request */
        if(rq->bRequest == USBRQ_HID_GET_REPORT){  /* wValue: ReportType (highbyte), ReportID (lowbyte) */
            /* since we have only one report type, we can ignore the report-ID */
            bytesRemaining = 128;
          currentAddress = 0;

            return USB_NO_MSG;  /* use usbFunctionRead() to obtain data */
        }else if(rq->bRequest == USBRQ_HID_SET_REPORT){
            /* since we have only one report type, we can ignore the report-ID */
            bytesRemaining = 128;
		          currentAddress = 0;
            return USB_NO_MSG;  /* use usbFunctionWrite() to receive data from host */
        }
    }else{
        /* ignore vendor type requests, we don't use any */
    }
    return 0;

}

int __attribute__((noreturn)) main(void)
{
	
uchar   i;
 setup();
     wdt_enable(WDTO_1S);
    /* Even if you don't use the watchdog, turn it off here. On newer devices,
     * the status of the watchdog (on/off, period) is PRESERVED OVER RESET!
     */
    /* RESET status: all port bits are inputs without pull-up.
     * That's the way we need D+ and D-. Therefore we don't need any
     * additional hardware initialization.
     */
    usbInit();
    usbDeviceDisconnect();  /* enforce re-enumeration, do this while interrupts are disabled! */
        i = 250;
    while(--i){             /* fake USB disconnect for > 250 ms */
          wdt_reset();
        _delay_ms(1);
    }
    usbDeviceConnect();
    //LED_PORT_DDR |= _BV(LED_BIT);   /* make the LED bit an output */
    sei();

    for(;;){                /* main event loop */
	wdt_reset();

	usbPoll();
	if (update == 1)
	{
		// Let's wait a bit
		ws2812_sendarray((uint8_t *)led,MAXPIX*3);
		update = 0;
	}

	if (update >1) {
		update--;
	}

	//loop();

    }
}

