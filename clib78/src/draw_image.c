#include "draw_image.h"
#include <time.h>

// Milliseconds since *lap, then moves *lap to now so consecutive calls time consecutive steps
static long lap_ms(struct timespec *lap) {
  struct timespec now;
  clock_gettime(CLOCK_MONOTONIC, &now);
  long elapsed = (now.tv_sec - lap->tv_sec) * 1000 + (now.tv_nsec - lap->tv_nsec) / 1000000;
  *lap = now;
  return elapsed;
}

static bool is_valid_area(const int *area, int panel_width, int panel_height) {
  const int x = area[0], y = area[1], w = area[2], h = area[3];
  return x >= 0 && y >= 0 && w > 0 && h > 0 && x + w <= panel_width && y + h <= panel_height && x % AREA_ALIGN == 0 && w % AREA_ALIGN == 0;
}

// Uploads the 8-bit image as is or packed to bits_per_pixel and starts a GC16 waveform on the area.
// image_8bit is the whole frame; areas holds area_count rectangles as x, y, w, h. A full refresh (init) or
// area_count 0 draws the whole panel.
int draw_image_8bit_areas(UBYTE *image_8bit, bool init, const int voltage, const int bits_per_pixel, const int *areas, const int area_count, t_logger logger) {
  if (bits_per_pixel != 8 && bits_per_pixel != 4 && bits_per_pixel != 2 && bits_per_pixel != 1) {
    logger(LOG_LEVEL_ERROR, L"Unsupported bit depth!");
    return 1;
  }

  // Not modified after setjmp, so it's still valid in cleanup after a longjmp
  struct timespec start;
  clock_gettime(CLOCK_MONOTONIC, &start);
  // Only read on the non-abort path
  struct timespec lap = start;

  // Init the BCM2835 Device
  logger(LOG_LEVEL_INFO, L"DEV_Module_Init()");

  if (DEV_Module_Init(logger) != 0) {
    logger(LOG_LEVEL_ERROR, L"DEV_Module_Init() failed");
    return 1;
  }

  int result = 0;
  // Volatile so the value is still valid after a longjmp from the driver
  UBYTE *volatile area_buffer = NULL;

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

  log_fmt(logger, LOG_LEVEL_INFO, L"Timing: DEV_Module_Init %ld ms", lap_ms(&lap));

  IT8951_Dev_Info Dev_Info = EPD_IT8951_Init(voltage, logger);
  log_fmt(logger, LOG_LEVEL_INFO, L"Timing: EPD_IT8951_Init %ld ms", lap_ms(&lap));

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

  const int full_area[4] = {0, 0, Panel_Width, Panel_Height};
  const bool whole_panel = init || area_count == 0;
  const int *draw_areas = whole_panel ? full_area : areas;
  const int draw_area_count = whole_panel ? 1 : area_count;

  // Check every area before drawing any, so a bad one doesn't leave the panel half updated
  for (int i = 0; i < draw_area_count; i++) {
    const int *area = &draw_areas[4 * i];
    if (!is_valid_area(area, Panel_Width, Panel_Height)) {
      log_fmt(logger, LOG_LEVEL_ERROR, L"Invalid area %d: x=%d y=%d w=%d h=%d", i, area[0], area[1], area[2], area[3]);
      result = 1;
      goto cleanup;
    }
  }

  if (init == true) {
    logger(LOG_LEVEL_INFO, L"EPD_IT8951_Init_Refresh()");
    EPD_IT8951_Init_Refresh(Dev_Info);
    log_fmt(logger, LOG_LEVEL_INFO, L"Timing: INIT command %ld ms", lap_ms(&lap));
    // The next refresh would wait for this anyway; waiting here separates the INIT waveform from the command timing
    EPD_IT8951_WaitForDisplayReady();
    log_fmt(logger, LOG_LEVEL_INFO, L"Timing: INIT waveform %ld ms", lap_ms(&lap));
  }

  for (int i = 0; i < draw_area_count; i++) {
    const int x = draw_areas[4 * i], y = draw_areas[4 * i + 1], w = draw_areas[4 * i + 2], h = draw_areas[4 * i + 3];
    log_fmt(logger, LOG_LEVEL_INFO, L"Area %d/%d: x=%d y=%d w=%d h=%d", i + 1, draw_area_count, x, y, w, h);

    area_buffer = pack_area(image_8bit, Panel_Width, x, y, w, h, bits_per_pixel);
    if (area_buffer == NULL) {
      logger(LOG_LEVEL_ERROR, L"Out of memory");
      result = 1;
      goto cleanup;
    }
    log_fmt(logger, LOG_LEVEL_INFO, L"Timing: conversion %ld ms", lap_ms(&lap));

    // Each refresh first waits for the previous area's waveform to finish
    if (bits_per_pixel == 8) {
      EPD_IT8951_8bp_Refresh(area_buffer, x, y, w, h, false, Memory_Addr, true);
    } else if (bits_per_pixel == 4) {
      EPD_IT8951_4bp_Refresh(area_buffer, x, y, w, h, false, Memory_Addr, true);
    } else if (bits_per_pixel == 2) {
      EPD_IT8951_2bp_Refresh(area_buffer, x, y, w, h, false, Memory_Addr, true);
    } else {
      EPD_IT8951_1bp_Refresh(area_buffer, x, y, w, h, GC16_Mode, Memory_Addr, true);
    }
    // 1 bpp waits for the waveform inside EPD_IT8951_Display_1bp, so its upload time includes the waveform.
    // From the second area on, the upload time also includes waiting for the previous area's waveform.
    log_fmt(logger, LOG_LEVEL_INFO, L"Timing: upload %ld ms", lap_ms(&lap));

    free(area_buffer);
    area_buffer = NULL;
  }

  logger(LOG_LEVEL_INFO, L"EPD_IT8951_WaitForDisplayReady()");
  EPD_IT8951_WaitForDisplayReady();
  log_fmt(logger, LOG_LEVEL_INFO, L"Timing: waveform %ld ms", lap_ms(&lap));
  EPD_IT8951_Sleep(logger);
  logger(LOG_LEVEL_INFO, L"Exiting cleanly");

cleanup:
  // Runs in the caller's process, so release everything on every path
  free(area_buffer);
  DEV_Module_Exit();
  log_fmt(logger, LOG_LEVEL_INFO, L"Timing: draw_image_8bit_areas total %ld ms", lap_ms(&start));
  return result;
}

// Packs one row of 8-bit pixels, keeping the top bits of each and putting the first pixel in the lowest bits.
// Inlined with a constant bits_per_pixel, so each bit depth gets its own unrolled loop.
static inline void pack_row(const UBYTE *in, UBYTE *out, size_t out_bytes, const int bits_per_pixel) {
  const int pixels_per_byte = 8 / bits_per_pixel;
  const UBYTE mask = (UBYTE)(0xFF << (8 - bits_per_pixel));
  for (size_t i = 0; i < out_bytes; i++) {
    UBYTE val = 0;
    for (int p = 0; p < pixels_per_byte; p++) {
      val |= (in[p] & mask) >> (8 - bits_per_pixel * (p + 1));
    }
    out[i] = val;
    in += pixels_per_byte;
  }
}

// Copies the area out of the 8-bit image (stride bytes per row) into a new buffer, packed to bits_per_pixel.
// w must be a multiple of 8 / bits_per_pixel. The caller frees the result.
UBYTE *pack_area(const UBYTE *image, size_t stride, int x, int y, int w, int h, int bits_per_pixel) {
  const size_t row_bytes = (size_t)w * bits_per_pixel / 8;
  UBYTE *buffer = malloc(row_bytes * h);
  if (buffer == NULL) {
    return NULL;
  }
  for (int row = 0; row < h; row++) {
    const UBYTE *in = image + (size_t)(y + row) * stride + x;
    UBYTE *out = buffer + (size_t)row * row_bytes;
    switch (bits_per_pixel) {
      case 8: memcpy(out, in, row_bytes); break;
      case 4: pack_row(in, out, row_bytes, 4); break;
      case 2: pack_row(in, out, row_bytes, 2); break;
      default: pack_row(in, out, row_bytes, 1); break;
    }
  }
  return buffer;
}
