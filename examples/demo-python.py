#! /usr/bin/env python
#
# Run like this:
# gitresman python demo-python.py

import sys
from time import sleep



def main():
    print 'This is logged (every line is logged when running in script mode)'

    for ii in range(3):
        print 'This is logged', ii
        print >>sys.stderr, 'This is logged (to stderr)', ii
        sleep(1)
    rundir = os.environ['GIT_RESULTS_MANAGER_DIR']
    with open(rundir + '/output_file_1.txt', 'w') as ff:
        ff.write('test output to file in results directory\n')

    print 'Run finished'



main()
