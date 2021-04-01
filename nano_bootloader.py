#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

resetPin = 26

GPIO.setmode(GPIO.BCM)

GPIO.setup(resetPin, GPIO.OUT)

GPIO.output(resetPin, GPIO.LOW)
time.sleep(0.1)
GPIO.output(resetPin, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(resetPin, GPIO.LOW)
time.sleep(0.1)
GPIO.output(resetPin, GPIO.HIGH)
