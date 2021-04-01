#include "draw_image.h"

int draw_image_8bit(UBYTE *image_8bit, bool init, const int bits_per_pixel, t_logger logger) {
  // Init the BCM2835 Device
  logger(LOG_LEVEL_INFO, L"DEV_Module_Init()");
  if (DEV_Module_Init(logger) != 0) {
    return 1;
  }

  logger(LOG_LEVEL_INFO, L"EPD_IT8951_Init()");
  IT8951_Dev_Info Dev_Info = EPD_IT8951_Init(1370, logger);

  // get some important info from Dev_Info structure
  UWORD Panel_Width = Dev_Info.Panel_W;
  UWORD Panel_Height = Dev_Info.Panel_H;
  UDOUBLE Memory_Addr = Dev_Info.Memory_Addr_L | (Dev_Info.Memory_Addr_H << 16);
  char *LUT_Version = (char *)Dev_Info.LUT_Version;

  if (strcmp(LUT_Version, "M841_TFA2812") == 0) {
    // 7.8inch e-Paper HAT(1872,1404)
    A2_Mode = 6;
  } else {
    return 1;
  }

  if (init == true) {
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_Init_Refresh()");
    EPD_IT8951_Init_Refresh(Dev_Info, Memory_Addr);
  }

  // logger(LOG_LEVEL_INFO, L"20 first data:");
  // for (size_t i = 0; i < 20; i++) {
  //   log_fmt(logger, LOG_LEVEL_DEBUG, L"Data = %X", image_8bit[i]);
  // }

  const size_t panel_size = Panel_Width * Panel_Height;

  if (bits_per_pixel == 8) {
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_8bp_Refresh()");
    EPD_IT8951_8bp_Refresh(image_8bit, 0, 0, Panel_Width, Panel_Height, false, Memory_Addr);
  } else if (bits_per_pixel == 4) {
    logger(LOG_LEVEL_INFO, L"from_8bit_to_4bit()");
    UBYTE *image_4bit = from_8bit_to_4bit(image_8bit, panel_size);
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_4bp_Refresh()");
    EPD_IT8951_4bp_Refresh(image_4bit, 0, 0, Panel_Width, Panel_Height, false, Memory_Addr, false);
    if (image_4bit != NULL) {
      free(image_4bit);
    }
  } else if (bits_per_pixel == 2) {

    logger(LOG_LEVEL_INFO, L"from_8bit_to_2bit()");
    UBYTE *image_2bit = from_8bit_to_2bit(image_8bit, panel_size);
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_2bp_Refresh()");
    EPD_IT8951_2bp_Refresh(image_2bit, 0, 0, Panel_Width, Panel_Height, false, Memory_Addr, false);
    if (image_2bit != NULL) {
      free(image_2bit);
    }
  } else if (bits_per_pixel == 1) {
    logger(LOG_LEVEL_INFO, L"from_8bit_to_1bit()");
    UBYTE *image_1bit = from_8bit_to_1bit(image_8bit, panel_size);
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_1bp_Refresh()");
    EPD_IT8951_1bp_Refresh(image_1bit, 0, 0, Panel_Width, Panel_Height, GC16_Mode, Memory_Addr,
                           false);
    if (image_1bit != NULL) {
      free(image_1bit);
    }
  } else {
    logger(LOG_LEVEL_ERROR, L"Unsupported bit depth!");
    return 1;
  }

  logger(LOG_LEVEL_INFO, L"EPD_IT8951_WaitForDisplayReady()");
  EPD_IT8951_WaitForDisplayReady();
  logger(LOG_LEVEL_INFO, L"EPD_IT8951_Sleep()");
  EPD_IT8951_Sleep();
  DEV_Module_Exit();
  return 0;
}

UBYTE *from_8bit_to_4bit(UBYTE *image, size_t size) {
  UBYTE *buffer = malloc(size / 2);
  UBYTE bit_mask = 0b11110000;
  for (size_t i = 0; i < size / 2; i++) {
    UBYTE val = ((image[2 * i] & bit_mask) >> 4) | ((image[2 * i + 1] & bit_mask) >> 0);
    buffer[i] = val;
  }
  return buffer;
}

UBYTE *from_8bit_to_2bit(UBYTE *image, size_t size) {
  UBYTE *buffer = malloc(size / 4);
  UBYTE bit_mask = 0b11000000;

  for (size_t i = 0; i < size / 4; i++) {
    UBYTE val = ((image[4 * i] & bit_mask) >> 6) | ((image[4 * i + 1] & bit_mask) >> 4) |
                ((image[4 * i + 2] & bit_mask) >> 2) | ((image[4 * i + 3] & bit_mask) >> 0);
    buffer[i] = val;
  }
  return buffer;
}

UBYTE *from_8bit_to_1bit(UBYTE *image, size_t size) {
  UBYTE *buffer = malloc(size / 8);
  UBYTE bit_mask = 0b10000000;
  for (size_t i = 0; i < size / 8; i++) {
    UBYTE val = ((image[8 * i] & bit_mask) >> 7) | ((image[8 * i + 1] & bit_mask) >> 6) |
                ((image[8 * i + 2] & bit_mask) >> 5) | ((image[8 * i + 3] & bit_mask) >> 4) |
                ((image[8 * i + 4] & bit_mask) >> 3) | ((image[8 * i + 5] & bit_mask) >> 2) |
                ((image[8 * i + 6] & bit_mask) >> 1) | ((image[8 * i + 7] & bit_mask) >> 0);
    buffer[i] = val;
  }
  return buffer;
}