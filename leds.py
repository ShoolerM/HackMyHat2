import board
import neopixel
import time
import random
import argparse
from datetime import datetime
import sys

import socket
import os

class Colors(object):
    def __init__(self, speed):
        self.NUM_LEDS = 707
        self.pixels = neopixel.NeoPixel(board.D18, self.NUM_LEDS, brightness=0.2, auto_write=False)
        self.wait_ms = speed
        self.color = self.rand_color()
        random.seed(datetime.now().timestamp())

    def rand_color(self):
        c = [
            ((255, 255, 255)),
            ((255,0,0)),
            ((0,255,0)),
            ((0,0,255)),
            ((0,255,255)),
            ((255,0,255)),
            ((255,255,0))
            ]
        return random.choice(c)

    def clear(self):
        self.color=((0,0,0))
        self.colorWipe()
        self.pixels.show()

    def colorWipe(self):
        for i in range(self.NUM_LEDS):
            self.pixels[i] = self.color
            if i%6 == 0:
                self.pixels.show()

    def blink(self):
        for i in range(3):
            self.pixels.fill((255, 255, 255))
            self.pixels.show()
            time.sleep(.5)
            self.pixels.fill((0,0,0))
            self.pixels.show()
            time.sleep(.5)

    def theaterChase(self):
        for q in range(1):
            for i in range(0, self.NUM_LEDS, 3):
                self.pixels[i+q%2] = self.color
                if i%4 == 0:
                    self.pixels.show()
            time.sleep(self.wait_ms/1000.0)
            for i in range(0, self.NUM_LEDS, 3):
                self.pixels[i+q%2] = ((0,0,0))
                if i%4 == 0:
                    self.pixels.show()
            time.sleep(self.wait_ms/1000.0)

    def wheel(self, pos):
        if pos < 85:
            return (((pos*3)&255, (255-pos*3)&255, 0))
        elif pos < 170:
            return (((255-pos*3)&255, 0, (pos*3)&255))
        else:
            pos-=170
            return ((0, (pos*3)&255, (255-pos*3)&255))

    def rainbow(self):
        for j in range(256):
            for i in range(self.NUM_LEDS):
                if j%5 == 0:
                    self.pixels[i] = self.wheel((i+j)&255)
            if j%5 == 0:
                self.pixels.show()

    def rainbowCycle(self):
        for j in range(2):
            for i in range(self.NUM_LEDS):
                if i%9 == 0:
                    self.pixels.fill(self.wheel(int(i*256 / self.NUM_LEDS)&255))
                    self.pixels.show()

    def rand(self):
        fill = []
        for i in range(int(self.NUM_LEDS)):
            fill.append(i)
        random.shuffle(fill)
        for i in fill:
            self.pixels[i] = ((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            if i %5 == 0:
                self.pixels.show()

    def solid_rand(self):
        fill = []
        for i in range(int(self.NUM_LEDS)):
            fill.append(i)
        random.shuffle(fill)
        for i in fill:
            self.pixels[i] = self.color
            if i%5 == 0:
                self.pixels.show()

    
    def rand_clear(self):
        fill = []
        for i in range(int(self.NUM_LEDS)):
            fill.append(i)
        random.shuffle(fill)
        for i in fill:
            self.pixels[i] = ((0, 0, 0))
            if i %5 == 0:
                self.pixels.show()
        self.allclear()

    def READING(self):
        self.pixels.fill((255,0,0))
        self.pixels.show()

    def DONE(self):
        for i in range(3):
            self.pixels.fill((0,255,0))
            self.pixels.show()
            time.sleep(.1)
            self.pixels.fill((0,0,0))
            self.pixels.show()
            time.sleep(.1)

        time.sleep(0.5)

    def allclear(self):
        self.pixels.fill((0,0,0))
        self.pixels.show()

def run_command(command):
    data = command.lower()
    commands = data.split(" ")
    c = None
    try:
        c = Colors(int(commands[0]))
        commands = commands[1:]
    except Exception as e:
        c = Colors(1)

    for action in commands:
        if action == "blink":
            c.blink()
        elif action == "color_wipe":
            c.colorWipe()
        elif action == "theater_chase":
            c.theaterChase()
        elif action == "rainbow":
            c.rainbow()
        elif action == "rainbow_cycle":
            c.rainbowCycle()
        elif action == "rand":
            c.rand()
        elif action == "solid_rand":
            c.solid_rand()
        elif action == "reading":
            c.READING()
        elif action == "done":
            c.DONE()
        elif action == "rand_clear":
            c.rand_clear()
        elif action == "allclear":
            c.allclear()
        elif action == "clear":
            c.clear()

def openSocket():
    sock_path = '/home/hat/ledsock'
    try:
        os.unlink(sock_path)
    except OSError:
        if os.path.exists(sock_path):
            raise
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(sock_path)
        s.listen(1)
        while True:
                c, a = s.accept()
                print("Connection made...")
                with c:
                    while True:
                        data = c.recv(1024)
                        if not data:
                            break
                        print(data)
                        run_command(data.decode())

if __name__ == "__main__":
    openSocket()
