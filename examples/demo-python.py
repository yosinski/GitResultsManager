#! /usr/bin/env python
#
# Run like this:
# gitresman python demo-python.py

import sys
import os
from time import sleep



def main():
    print('This is logged (every line is logged when running in script mode)')

    for ii in range(3):
        print('This is logged', ii)
        print('This is logged (to stderr)', ii, file=sys.stderr)
        sleep(1)
    try:
        rundir = os.environ['GIT_RESULTS_MANAGER_DIR']
    except KeyError:
        print('\nEnvironment variable GIT_RESULTS_MANAGER_DIR is undefined. To demonstrate logging, run this instead as\n   gitresman junk ./demo-python.py', file=sys.stderr)
        sys.exit(1)

    with open(rundir + '/output_file_1.txt', 'w') as ff:
        ff.write('test output to file in results directory\n')

    print('Run finished')



main()
