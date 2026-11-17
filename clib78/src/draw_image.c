#include "draw_image.h"

int draw_image_8bit(UBYTE *image_8bit, bool init, const int voltage, const int bits_per_pixel, t_logger logger) {
  // Init the BCM2835 Device
  logger(LOG_LEVEL_INFO, L"DEV_Module_Init()");

  if (DEV_Module_Init(logger) != 0) {
    logger(LOG_LEVEL_ERROR, L"DEV_Module_Init() failed");
    return 1;
  }

  int result = 0;
  // Volatile so the value is still valid after a longjmp from the driver
  UBYTE *volatile image_converted = NULL;

  // The driver jumps back here if the controller stops responding
  if (setjmp(EPD_IT8951_Abort_Jmp) != 0) {
    result = EPD_IT8951_Abort_Code;
    if (result == EPD_IT8951_BUSY_TIMEOUT) {
      log_fmt(logger, LOG_LEVEL_ERROR, L"Timed out after %d ms waiting for the busy pin", EPD_IT8951_BUSY_TIMEOUT_MS);
    } else {
      log_fmt(logger, LOG_LEVEL_ERROR, L"Timed out after %d ms waiting for the display to be ready", EPD_IT8951_DISPLAY_READY_TIMEOUT_MS);
    }
    goto cleanup;
  }

  IT8951_Dev_Info Dev_Info = EPD_IT8951_Init(voltage, logger);

  // get some important info from Dev_Info structure
  UWORD Panel_Width = Dev_Info.Panel_W;
  UWORD Panel_Height = Dev_Info.Panel_H;
  UDOUBLE Memory_Addr = Dev_Info.Memory_Addr_L | (Dev_Info.Memory_Addr_H << 16);
  char *LUT_Version = (char *)Dev_Info.LUT_Version;

  if (strcmp(LUT_Version, "M841_TFA2812") == 0 || strcmp(LUT_Version, "M841_TFA5210") == 0) {
    // 7.8inch e-Paper HAT(1872,1404) - M841_TFA2812
    //10.3inch e-Paper HAT(1872,1404) - M841_TFA5210
    A2_Mode = 6;
  } else {
    logger(LOG_LEVEL_WARNING, L"Unsupported LUT_Version");
    result = 1;
    goto cleanup;
  }

  if (init == true) {
    EPD_IT8951_Init_Refresh(Dev_Info, Memory_Addr, true);
  }

  const size_t panel_size = Panel_Width * Panel_Height;

  if (bits_per_pixel == 8) {
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_8bp_Refresh()");
    EPD_IT8951_8bp_Refresh(image_8bit, 0, 0, Panel_Width, Panel_Height, false, Memory_Addr);
  } else if (bits_per_pixel == 4 || bits_per_pixel == 2 || bits_per_pixel == 1) {
    log_fmt(logger, LOG_LEVEL_INFO, L"from_8bit_to_%dbit()", bits_per_pixel);
    image_converted = bits_per_pixel == 4 ? from_8bit_to_4bit(image_8bit, panel_size)
                    : bits_per_pixel == 2 ? from_8bit_to_2bit(image_8bit, panel_size)
                                          : from_8bit_to_1bit(image_8bit, panel_size);
    if (image_converted == NULL) {
      logger(LOG_LEVEL_ERROR, L"Out of memory");
      result = 1;
      goto cleanup;
    }
    log_fmt(logger, LOG_LEVEL_INFO, L"EPD_IT8951_%dbp_Refresh()", bits_per_pixel);
    if (bits_per_pixel == 4) {
      EPD_IT8951_4bp_Refresh(image_converted, 0, 0, Panel_Width, Panel_Height, false, Memory_Addr, true);
    } else if (bits_per_pixel == 2) {
      EPD_IT8951_2bp_Refresh(image_converted, 0, 0, Panel_Width, Panel_Height, false, Memory_Addr, true);
    } else {
      EPD_IT8951_1bp_Refresh(image_converted, 0, 0, Panel_Width, Panel_Height, GC16_Mode, Memory_Addr, true);
    }
  } else {
    logger(LOG_LEVEL_ERROR, L"Unsupported bit depth!");
    result = 1;
    goto cleanup;
  }

  logger(LOG_LEVEL_INFO, L"EPD_IT8951_WaitForDisplayReady()");
  EPD_IT8951_WaitForDisplayReady();
  EPD_IT8951_Sleep(logger);
  logger(LOG_LEVEL_INFO, L"Exiting cleanly");

cleanup:
  // Runs in the caller's process, so release everything on every path
  free(image_converted);
  DEV_Module_Exit();
  return result;
}

UBYTE *from_8bit_to_4bit(UBYTE *image, size_t size) {
  UBYTE *buffer = malloc(size / 2);
  if (buffer == NULL) {
    return NULL;
  }
  UBYTE bit_mask = 0b11110000;
  for (size_t i = 0; i < size / 2; i++) {
    UBYTE val = ((image[2 * i] & bit_mask) >> 4) | ((image[2 * i + 1] & bit_mask) >> 0);
    buffer[i] = val;
  }
  return buffer;
}

UBYTE *from_8bit_to_2bit(UBYTE *image, size_t size) {
  UBYTE *buffer = malloc(size / 4);
  if (buffer == NULL) {
    return NULL;
  }
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
  if (buffer == NULL) {
    return NULL;
  }
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