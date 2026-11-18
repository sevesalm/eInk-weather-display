DIR_Config   = ./lib/Config
DIR_EPD      = ./lib/e-Paper
DIR_Src 		 = ./src

DIR_BIN      = ./bin

OBJ_C = $(wildcard ${DIR_Config}/*.c ${DIR_EPD}/*.c ${DIR_Src}/*.c )
OBJ_O = $(patsubst %.c,${DIR_BIN}/%.o,$(notdir ${OBJ_C}))

TARGET = epd78.so

CC = gcc

# Frame buffers are written as bytes and read back as UWORDs, so keep strict aliasing off.
# Debug.h checks DEBUG, e.g. `make DEBUG=-DDEBUG` for file/line in Debug() output.
MSG = -O2 -fno-strict-aliasing -Wall
DEBUG =
STD = # -std=c99 <--- Removed for off_t error

CFLAGS += $(MSG) $(DEBUG) $(STD) -fPIC 

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

