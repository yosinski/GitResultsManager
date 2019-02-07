#! /usr/bin/env python

from __future__ import print_function

from time import sleep
from datetime import datetime, timedelta
import random
import sys

def snoozer():
    print('This program sleeps for deterministic durations, periodically waking up to print the approximate time. Runs until reaching its time limit (3 seconds by default).')
    
    if len(sys.argv) > 1:
        maxTime = float(sys.argv[1])
    else:
        maxTime = 3
        
    time = 0.0
    while True:
        sleep(.3)
        time += .3
        print(time)
        sys.stdout.flush()
        if time > maxTime:
            break

snoozer()
