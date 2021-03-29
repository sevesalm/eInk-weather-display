#ifndef _LOGGER_H
#define _LOGGER_H
#include <stdarg.h>
#include <stddef.h>

enum { LOG_LEVEL_DEBUG = 10, LOG_LEVEL_INFO = 20, LOG_LEVEL_WARNING = 30, LOG_LEVEL_ERROR = 40 };
typedef void (*t_logger)(int log_level, wchar_t *msg);
void log_fmt(t_logger logger, const int log_level, const wchar_t *fmt, ...);

#endif