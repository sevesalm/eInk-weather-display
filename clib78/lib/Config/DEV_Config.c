/*****************************************************************************
* | File      	:   DEV_Config.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*----------------
* |	This version:   V3.0
* | Date        :   2019-09-17
* | Info        :   
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of theex Software, and to permit persons to  whom the Software is
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
#include "DEV_Config.h"
#include <fcntl.h>

/******************************************************************************
function:	GPIO Write
parameter:
Info:
******************************************************************************/
void DEV_Digital_Write(UWORD Pin, UBYTE Value)
{
	bcm2835_gpio_write(Pin, Value);
}

/******************************************************************************
function:	GPIO Read
parameter:
Info:
******************************************************************************/
UBYTE DEV_Digital_Read(UWORD Pin)
{
	UBYTE Read_Value = 0;
	Read_Value = bcm2835_gpio_lev(Pin);
	return Read_Value;
}

/******************************************************************************
function:	SPI Write
parameter:
Info:
******************************************************************************/
void DEV_SPI_WriteByte(UBYTE Value)
{
	bcm2835_spi_transfer(Value);
}

/******************************************************************************
function:	SPI Write multiple bytes in one transfer
parameter:
Info:		Runs at DEV_SPI_WRITE_CLOCK_DIVIDER, then restores the default clock
******************************************************************************/
void DEV_SPI_WriteBytes(const char *Buf, uint32_t Length)
{
	bcm2835_spi_setClockDivider(DEV_SPI_WRITE_CLOCK_DIVIDER);
	bcm2835_spi_writenb(Buf, Length);
	bcm2835_spi_setClockDivider(DEV_SPI_CLOCK_DIVIDER);
}

/******************************************************************************
function:	SPI Read
parameter:
Info:
******************************************************************************/
UBYTE DEV_SPI_ReadByte()
{
	UBYTE Read_Value = 0x00;
	Read_Value = bcm2835_spi_transfer(0x00);
	return Read_Value;
}

/******************************************************************************
function:	Time delay for ms
parameter:
Info:
******************************************************************************/
void DEV_Delay_ms(UDOUBLE xms)
{
	bcm2835_delay(xms);
}

/******************************************************************************
function:	Time delay for us
parameter:
Info:
******************************************************************************/
void DEV_Delay_us(UDOUBLE xus)
{
	bcm2835_delayMicroseconds(xus);
}

/**
 * GPIO Mode
**/
static void DEV_GPIO_Mode(UWORD Pin, UWORD Mode)
{
	if (Mode == 0 || Mode == BCM2835_GPIO_FSEL_INPT)
	{
		bcm2835_gpio_fsel(Pin, BCM2835_GPIO_FSEL_INPT);
	}
	else
	{
		bcm2835_gpio_fsel(Pin, BCM2835_GPIO_FSEL_OUTP);
	}
}

/**
 * GPIO Init
**/
static void DEV_GPIO_Init(void)
{
	// Set the output levels before switching the pins to outputs, so RST never glitches low and resets
	// a controller that was left in SLEEP by the previous call
	DEV_Digital_Write(EPD_RST_PIN, HIGH);
	DEV_Digital_Write(EPD_CS_PIN, HIGH);

	DEV_GPIO_Mode(EPD_RST_PIN, BCM2835_GPIO_FSEL_OUTP);
	DEV_GPIO_Mode(EPD_CS_PIN, BCM2835_GPIO_FSEL_OUTP);
	DEV_GPIO_Mode(EPD_BUSY_PIN, BCM2835_GPIO_FSEL_INPT);
}

/******************************************************************************
function:	Module Initialize, the library and initialize the pins, SPI protocol
parameter:
Info:
******************************************************************************/
UBYTE DEV_Module_Init(t_logger logger)
{
	// See: https://www.airspayce.com/mikem/bcm2835/group__constants.html#gaf2e0ca069b8caef24602a02e8a00884e
	log_fmt(logger, LOG_LEVEL_DEBUG, L"SPI Clock Divider = %d, bulk write divider = %d", DEV_SPI_CLOCK_DIVIDER, DEV_SPI_WRITE_CLOCK_DIVIDER);

	if (!bcm2835_init())
	{
		logger(LOG_LEVEL_ERROR, L"bcm2835_init() failed");
		return 1;
	}

	bcm2835_spi_begin();																		 //Start spi interface, set spi pin for the reuse function
	bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST); //High first transmission
	bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);							 //spi mode 0
	bcm2835_spi_setClockDivider(DEV_SPI_CLOCK_DIVIDER);
	/* SPI clock reference link：*/
	/*http://www.airspayce.com/mikem/bcm2835/group__constants.html#gaf2e0ca069b8caef24602a02e8a00884e*/

	//GPIO Config
	DEV_GPIO_Init();
	return 0;
}

/******************************************************************************
function:	Module exits, closes SPI and BCM2835 library
parameter:
Info:		Leaves RST high so the controller stays in SLEEP between calls instead of being held in reset,
		and CS high (deselected)
******************************************************************************/
void DEV_Module_Exit(void)
{
	DEV_Digital_Write(EPD_CS_PIN, HIGH);
	DEV_Digital_Write(EPD_RST_PIN, HIGH);

	bcm2835_spi_end();
	bcm2835_close();
}
