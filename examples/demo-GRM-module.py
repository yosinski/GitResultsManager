#! /usr/bin/env python

import sys
from time import sleep
from GitResultsManager import resman



def main():
    print('Run about to start (not logged because run has not yet started)')

    resman.start('demo-GRM-module-run')

    for ii in range(3):
        print('This is logged', ii)
        print('This is logged (to stderr)', ii, file=sys.stderr)
        sleep(1)
    with open(resman.rundir + '/output_file_1.txt', 'w') as ff:
        ff.write('test direct output to file in results directory\n')

    resman.stop()

    print('Run finished (not logged because run is over)')



if __name__ == '__main__':
    main()
