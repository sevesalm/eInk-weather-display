/*****************************************************************************
* | File      	:   EPD_3IN7_test.c
* | Author      :   Waveshare team
* | Function    :   3.7inch e-paper test demo
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2020-07-16
* | Info        :
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#include "logger.h"
#include "draw_image.h"
#include "EPD_3in7.h"

void sleep_and_exit(t_logger logger) {
    logger(LOG_LEVEL_INFO, L"Sleeping");
    EPD_3IN7_Sleep(); // Sleep & close 5V
    logger(LOG_LEVEL_INFO, L"Delaying (2000 ms)");
    DEV_Delay_ms(2000); //important, at least 2s
    logger(LOG_LEVEL_INFO, L"DEV_Module_Exit()");
    DEV_Module_Exit();
    return;
}

int draw_image_2bit(UBYTE *image, t_logger logger) {
    logger(LOG_LEVEL_INFO, L"DEV_Module_Init()");
    if(DEV_Module_Init(logger) != 0){
        return -1;
    }
    logger(LOG_LEVEL_INFO, L"Initializing 2-bit mode");
	EPD_3IN7_4Gray_Init();
    logger(LOG_LEVEL_INFO, L"Drawing");
    EPD_3IN7_4Gray_Display(image);
    sleep_and_exit(logger);
    return 0;
}

int draw_image_1bit(UBYTE *image, t_logger logger) {
    int mode = 1;
    logger(LOG_LEVEL_INFO, L"DEV_Module_Init()");
    if(DEV_Module_Init(logger) != 0){
        return -1;
    }
    logger(LOG_LEVEL_INFO, L"Initializing 1-bit mode");
	EPD_3IN7_1Gray_Init();

    logger(LOG_LEVEL_INFO, L"Clearing");
    EPD_3IN7_1Gray_Clear(mode);

    logger(LOG_LEVEL_INFO, L"Drawing");
    EPD_3IN7_1Gray_Display(image, mode);
    sleep_and_exit(logger);
    return 0;
}