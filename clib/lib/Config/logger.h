#ifndef _DRAW_IMAGE_H_
#define _DRAW_IMAGE_H_
#include <stddef.h>

enum { LOG_LEVEL_DEBUG = 10, LOG_LEVEL_INFO = 20, LOG_LEVEL_WARNING = 30, LOG_LEVEL_ERROR = 40 };

typedef void (*t_logger)(int, wchar_t *);
#endif