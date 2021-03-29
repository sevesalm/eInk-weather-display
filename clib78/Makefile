DIR_Config   = ./lib/Config
DIR_EPD      = ./lib/e-Paper
DIR_Src 		 = ./src

DIR_BIN      = ./bin

OBJ_C = $(wildcard ${DIR_Config}/*.c ${DIR_EPD}/*.c ${DIR_Src}/*.c )
OBJ_O = $(patsubst %.c,${DIR_BIN}/%.o,$(notdir ${OBJ_C}))

TARGET = epd78.so

CC = gcc

MSG = -g -O0 -Wall
DEBUG = -D USE_DEBUG
STD = # -std=c99 <--- Removed for off_t error

CFLAGS += $(MSG) $(DEBUG) $(STD)

LIB = -lbcm2835 -lm -lrt -lpthread

$(shell mkdir -p $(DIR_BIN))

${TARGET}:${OBJ_O}
	$(CC) $(CFLAGS) -shared -fPIC $(OBJ_O) -o $@ $(LIB)

${DIR_BIN}/%.o:$(DIR_Config)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@ 

${DIR_BIN}/%.o:$(DIR_EPD)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@
	
${DIR_BIN}/%.o:$(DIR_Src)/%.c
	$(CC) $(CFLAGS) -c  $< -o $@

clean :
	rm $(DIR_BIN)/*.* 
	rm $(TARGET) 

