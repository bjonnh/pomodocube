/*
 *
 * This example is configured for an Atmega85 at 16.5MHz
 */ 

#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include "light_ws2812.h"
#include <avr/pgmspace.h>
#include "usbdrv.h"
#include "requests.h"
#include <avr/wdt.h>
#include <string.h>
#include "osccal.h"
#include "colors.h"
#include "sine.h"

#define sei() asm volatile("sei")
#define cli() asm volatile("cli")
#define nop() asm volatile("nop")

#define MAXPIX 8

struct cRGB led[MAXPIX];

uint8_t update=0;
uint8_t brightness=128;
uint8_t anim_frame=0;

#define PARAMSIZE 8
uchar param[PARAMSIZE];

static uchar    currentAddress;
static uchar    bytesRemaining;

//
// Update the leds
//

void update_leds(void) {
  ws2812_sendarray_mask((uint8_t *)led,MAXPIX*3, _BV(ws2812_pin));
}

//
// Copy the src color to dest taking brightness into account
//

void copy_color(Color *dest, Color *src) {
  // Copy color according to global brightness
  uint16_t r,g,b;
  g =  brightness * src->g / 256;
  r = brightness * src->r /256;
  b = brightness * src->b /256;
  dest->g = g;
  dest->r = r;
  dest->b = b;
}

//
// Set the specified color to the specified preset
//

void copy_preset_color(Color *dest, uint8_t preset) {
  Color src = {pgm_read_byte(&(colors[preset%COLORS_PRESET].g)),
		     pgm_read_byte(&(colors[preset%COLORS_PRESET].r)),
		     pgm_read_byte(&(colors[preset%COLORS_PRESET].b))};
  copy_color(dest, &src); 
}

//
// Copy these rgb values inside the dest color
//

void copy_rgb_color(Color *dest, uint8_t r, uint8_t g, uint8_t b) {
  Color src = {g,r,b};
  copy_color(dest, &src); 
}

//
// A boot animation optimized for 8 leds
//

void boot_animation(void) {
  for(uint8_t i=MAXPIX; i>0; i--) {
    copy_rgb_color(&(led[i-1]),
		   0,
		   pgm_read_byte(&(sine[((i*64/MAXPIX)+(128+anim_frame))%256])),
		   pgm_read_byte(&(sine[((i*64/MAXPIX)+(128+anim_frame))%256])));
  }
  anim_frame++;
  update_leds();
}


//
// This is the main function that reacts to parameters according to:
// Commands
// 00  . . . . . . . : Reset to black
// 01  r g b . . . . : Set all to color r g b
// 02  r g b l . . . : Set led l to color r g b
// 03  c . . . . . . ; Set all to color preset c
// 04  c l . . . . . ; Set l to color preset c
// f0  b . . . . . . ; Set brightness (applied at next color setting)
//

void react(void) {
  uint8_t i;

  switch (param[0]) {
  case 0: // Set off all
    for(i=MAXPIX; i>0; i--)
      {
	copy_preset_color(&(led[i-1]), 0);
      }
		
    update=1;

    break;
  case 1: // Full color
    for(i=MAXPIX; i>0; i--)
      {
	copy_rgb_color(&(led[i-1]), param[1], param[2], param[3]);
      }

    update=1;
    break;
  case 2: // Set
    copy_rgb_color(&(led[param[4]%MAXPIX]), param[1], param[2], param[3]);
    update=1;
    break;


 case 3: // Full color with preset
    for(i=MAXPIX; i>0; i--)
      {
	copy_preset_color(&(led[i-1]), param[1]);
      }

    update=1;
    break;
  case 4: // Set one with preset
    copy_preset_color(&(led[param[2]%MAXPIX]), param[1]);

    update=1;
    break;
  case 0xf0: // Set brightness
    brightness = param[1];
    break;
  }
}

void go_black(void)
{
  for (uint8_t i=0;i<PARAMSIZE;i++) {
    param[i]=0;
  }
  react();
}

PROGMEM const char usbHidReportDescriptor[22] = {    /* USB report descriptor */
  0x06, 0x00, 0xff,              // USAGE_PAGE (Generic Desktop)
  0x09, 0x01,                    // USAGE (Vendor Usage 1)
  0xa1, 0x01,                    // COLLECTION (Application)
  0x15, 0x00,                    //   LOGICAL_MINIMUM (0)
  0x26, 0xff, 0x00,              //   LOGICAL_MAXIMUM (255)
  0x75, 0x08,                    //   REPORT_SIZE (8)
  0x95, 0x01,                    //   REPORT_COUNT (1)
  0x09, 0x00,                    //   USAGE (Undefined)
  0xb2, 0x02, 0x01,              //   FEATURE (Data,Var,Abs,Buf)
  0xc0                           // END_COLLECTION
};
uchar   usbFunctionRead(uchar *data, uchar len)
{
  if (len > bytesRemaining)
    len = bytesRemaining;
  for (uint8_t i=0; i<len; i++) {
    data[i] = param[i];
  }
  currentAddress += len;
  bytesRemaining -= len;
  return len;
}

uchar   usbFunctionWrite(uchar *data, uchar len)
{
  memcpy(param, data, len);
  react();
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
void __attribute__ ((noreturn)) main() 
{	
  uchar i;

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

  i = 255;
  while(--i){             /* fake USB disconnect for > 250 ms */
    wdt_reset();
    _delay_ms(1);
    boot_animation();
  }
  usbDeviceConnect();

  sei();
  go_black();
  for(;;){                /* main event loop */
    wdt_reset();

    usbPoll();
    if (update >= 1)
      {
	update_leds();
	update = 0;
      }
  }
}

