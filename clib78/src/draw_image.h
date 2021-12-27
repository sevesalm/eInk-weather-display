#ifndef _DRAW_IMAGE_H_
#define _DRAW_IMAGE_H_

#include "../lib/Config/DEV_Config.h"
#include "../lib/Config/logger.h"
#include "../lib/e-Paper/EPD_IT8951.h"

int draw_image_8bit(UBYTE *image, bool init, const int voltage, const int bits_per_pixel, t_logger logger);
UBYTE *from_8bit_to_4bit(UBYTE *image, size_t size);
UBYTE *from_8bit_to_2bit(UBYTE *image, size_t size);
UBYTE *from_8bit_to_1bit(UBYTE *image, size_t size);
#endif