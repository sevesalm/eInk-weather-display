#include "logger.h"
#include <wchar.h>

void log_fmt(t_logger logger, const int log_level, const wchar_t *fmt, ...) {
  va_list args;
  va_start(args, fmt);
  const int buffer_size = 100;
  wchar_t buffer[buffer_size];
  vswprintf(buffer, buffer_size, fmt, args);
  va_end(args);
  logger(LOG_LEVEL_DEBUG, buffer);
}