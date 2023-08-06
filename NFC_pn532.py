import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.spi import PN532_SPI

from leds import Colors
import socket
import time
import binascii

# SPI connection:
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)


ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

#main loop
while True:
    while True:
        # Check if a card is available to read
        uid = None
        uid = pn532.read_passive_target(timeout=0.5)
        #print(".", end="")
        # Try again if no card is available.
        if uid is not None:
            break
    try:
        leds = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        leds.connect('/home/hat/ledsock')
    except Exception as e:
        print("ERROR CONNECTING TO LEDSOCK")
        raise

    try:
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_address = '/home/hat/hatsock'
        server_sock.connect(server_address)
    except Exception as e:
        print("ERROR CONNECTING TO HATSOCK")
        raise

    leds.sendall(b"reading")

    out = ""
    ch = 0xFF
    block_num = 0
    #Gotta initialize
    block = pn532.ntag2xx_read_block(0)
    block_lock = 1
    while(ch):
        block = pn532.ntag2xx_read_block(block_num)
        block_num += 1

        if block and block_lock != 0:
            if block[2] == 0x02 and block[3] == 0x65:
                block_lock = 0
                out = out + chr(block[2])
                out = out + chr(block[3])
                continue
            else:
                continue
            
        if block:
            for x in block:
                if x < 32 or x > 126:
                    ch = 0
                else:
                    out = out + chr(x)
        else:
            ch = 0

    #Clear out start bytes
    out = out[3:]

    b_out = bytes(out, 'ascii')
    b_out += b"\x00"
    leds.sendall(b"done")
    leds.close()
    server_sock.send(b_out)
    time.sleep(2)
