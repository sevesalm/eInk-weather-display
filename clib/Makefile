DIR_Config   = ./lib/Config
DIR_e-Paper  = ./lib/e-Paper
DIR_Src = ./src
DIR_BIN = ./bin

OBJ_C = $(wildcard ${DIR_e-Paper}/*.c ${DIR_Src}/*.c )
OBJ_O = $(patsubst %.c,${DIR_BIN}/%.o,$(notdir ${OBJ_C}))
RPI_DEV_C = $(wildcard  $(DIR_BIN)/DEV_Config.o )

# DEBUG = -D DEBUG

LIB_RPI=-Wl,--gc-sections,-lbcm2835,-lm 
DEBUG_RPI = -D RPI

.PHONY : RPI clean

RPI:RPI_DEV RPI_epd 

TARGET = epd
CC = gcc
MSG = -g -O -ffunction-sections -fdata-sections -Wall
CFLAGS += $(MSG)

RPI_epd:${OBJ_O}
	$(CC) $(CFLAGS) -shared -fPIC -D RPI $(OBJ_O) -o epd.so $(RPI_DEV_C) $(LIB_RPI) $(DEBUG)
    
$(shell mkdir -p $(DIR_BIN))

${DIR_BIN}/%.o:$(DIR_Src)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ -I $(DIR_Config) -I $(DIR_e-Paper) $(DEBUG)
    
${DIR_BIN}/%.o:$(DIR_e-Paper)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ -I $(DIR_Config) $(DEBUG)
    
RPI_DEV:
	$(CC) $(CFLAGS) $(DEBUG_RPI) -c  $(DIR_Config)/DEV_Config.c -o $(DIR_BIN)/DEV_Config.o $(LIB_RPI) $(DEBUG)
	
clean :
	rm $(DIR_BIN)/*.* 
	rm $(TARGET) 

