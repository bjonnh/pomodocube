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

#define MAXPIX 8

struct cRGB colors[8];
struct cRGB led[MAXPIX];

usbMsgLen_t usbFunctionSetup(uchar data[8])
{
usbRequest_t    *rq = (void *)data;
static uchar    dataBuffer[4];  /* buffer must stay valid when usbFunctionSetup returns */

    if(rq->bRequest == CUSTOM_RQ_ECHO){ /* echo -- used for reliability tests */
        dataBuffer[0] = rq->wValue.bytes[0];
        dataBuffer[1] = rq->wValue.bytes[1];
        dataBuffer[2] = rq->wIndex.bytes[0];
        dataBuffer[3] = rq->wIndex.bytes[1];
        usbMsgPtr = dataBuffer;         /* tell the driver which data to return */
        return 4;
    }else if(rq->bRequest == CUSTOM_RQ_SET_STATUS){
        if(rq->wValue.bytes[0] & 1){    /* set LED */
	  //LED_PORT_OUTPUT |= _BV(LED_BIT);
        }else{                          /* clear LED */
	  //LED_PORT_OUTPUT &= ~_BV(LED_BIT);
        }
    }else if(rq->bRequest == CUSTOM_RQ_GET_STATUS){
      dataBuffer[0] = 42; //((LED_PORT_OUTPUT & _BV(LED_BIT)) != 0);
        usbMsgPtr = dataBuffer;         /* tell the driver which data to return */
        return 1;                       /* tell the driver to send 1 byte */
    }
    return 0;   /* default for not implemented requests: return no data back to host */
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
    odDebugInit();
    DBG1(0x00, 0, 0);       /* debug output: main starts */
    usbInit();
    usbDeviceDisconnect();  /* enforce re-enumeration, do this while interrupts are disabled! */
        i = 0;
    while(--i){             /* fake USB disconnect for > 250 ms */
          wdt_reset();
        _delay_ms(1);
    }
    usbDeviceConnect();
    //LED_PORT_DDR |= _BV(LED_BIT);   /* make the LED bit an output */
    sei();
    DBG1(0x01, 0, 0);       /* debug output: main loop starts */
    for(;;){                /* main event loop */
        DBG1(0x02, 0, 0);   /* debug output: main loop iterates */
		        wdt_reset();
        usbPoll();
					loop();
    }
}


	uint8_t j = 1;
	uint8_t k = 1;

int setup(void)
{
	

	DDRB|=_BV(ws2812_pin);
		
    uint8_t i;
    for(i=MAXPIX; i>0; i--)
    {    
        led[i-1].r=0;led[i-1].g=0;led[i-1].b=0;
    }
		
    //Rainbowcolors
    colors[0].r=150; colors[0].g=150; colors[0].b=150;
    colors[1].r=255; colors[1].g=000; colors[1].b=000;//red
    colors[2].r=255; colors[2].g=100; colors[2].b=000;//orange
    colors[3].r=100; colors[3].g=255; colors[3].b=000;//yellow
    colors[4].r=000; colors[4].g=255; colors[4].b=000;//green
    colors[5].r=000; colors[5].g=100; colors[5].b=255;//light blue (türkis)
    colors[6].r=000; colors[6].g=000; colors[6].b=255;//blue
    colors[7].r=100; colors[7].g=000; colors[7].b=255;//violet
}
#define LOOPS 640
uint16_t loopy=0;
uint8_t col=0;
int loop(void)
{
  if (loopy<LOOPS) {
    loopy++;
  } else {
    loopy=0;
    for (uint8_t i=MAXPIX;i>0;i--)
      {
	led[i-1].r=colors[(i%8+col)-1].r;
	led[i-1].g=colors[(i%8+col)-1].g;
	led[i-1].b=colors[(i%8+col)-1].b;

      }
    if(col<7) {col++;} else {col=0;}
 ws2812_sendarray((uint8_t *)led,MAXPIX*3);
				 //		 sei();
				 //wdt_reset();
  }  
}
