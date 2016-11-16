typedef struct cRGB Color;
#define COLORS_PRESET 8
// They are coded as g,r,b !
const Color colors[COLORS_PRESET] PROGMEM={{0,0,0}, // black
						 {0,255,0}, // red
						 {255,0,0}, // green
						 {0,0,255}, // blue
						 {255,255,0}, // yellow
						 {0,255,255}, // purple
						 {255,0,255}, // cyan
						 {255,255,255} // white
};
