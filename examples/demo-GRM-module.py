#! /usr/bin/env python

from __future__ import print_function

import sys
from time import sleep
from GitResultsManager import resman



def main():
    print('This is not logged')

    resman.start('demo-GRM-module-run')

    for ii in range(3):
        print('This is logged', ii)
        print('This is logged (to stderr)', ii, file=sys.stderr)
        sleep(1)
    with open(resman.rundir + '/output_file_1.txt', 'w') as ff:
        ff.write('test output to file in results directory\n')

    resman.stop()

    print('Run finished')



main()
