#!/bin/bash
amixer -c 1 cset numid=3 120,120
aplay -D default:CARD=UACDemoV10 ./yeehaw.wav
