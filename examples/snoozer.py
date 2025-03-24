#! /usr/bin/env python

from time import sleep
from datetime import datetime, timedelta
import random
import sys


def snoozer():
    print('This program sleeps for deterministic durations, periodically waking up to print the elapsed time. Runs until reaching its time limit (3 seconds by default).')
    
    if len(sys.argv) > 1:
        maxTime = float(sys.argv[1])
    else:
        maxTime = 3
        
    time = 0.0
    while True:
        print(f'Script has run for {time:.1f} seconds.')
        time += .3
        if time > maxTime:
            break
        sleep(.3)


if __name__ == '__main__':
    snoozer()
