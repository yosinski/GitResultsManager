#! /usr/bin/env python

import sys
from time import sleep
from GitResultsManager import resman



def main():
    print 'This is not logged'

    resman.start('demo-GRM-module-run')

    for ii in range(3):
        print 'This is logged', ii
        print >>sys.stderr, 'This is logged (to stderr)', ii
        sleep(1)

    resman.stop()

    print 'Run finished'



main()
