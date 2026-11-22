#ifndef _DRAW_IMAGE_H_
#define _DRAW_IMAGE_H_

#include "../lib/Config/DEV_Config.h"
#include "../lib/Config/logger.h"
#include "../lib/e-Paper/EPD_IT8951.h"

// Area x and width must be multiples of this so every bit depth packs whole words per row (1 bpp needs 16 px).
// Must match AREA_ALIGN in display_areas.py.
#define AREA_ALIGN 16

int draw_image_8bit_areas(UBYTE *image, bool init, const int voltage, const int bits_per_pixel, const int *areas, const int area_count, t_logger logger);
UBYTE *pack_area(const UBYTE *image, size_t stride, int x, int y, int w, int h, int bits_per_pixel);
#endif
