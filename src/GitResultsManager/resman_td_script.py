#! /usr/bin/env python

'''
Compute time difference between two lines of resman output. See usage.
'''

import traceback
import sys
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='Computes time differences between lines of resman output.\nUsage: Put lines on stdin or in a file whose filename is the first argument.')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print e.g. a "No file given..." message when reading from stdin.')
    parser.add_argument('--total', '-t', action='store_true',
                        help='Instead of time diffs between each line, print a running total time since the beginning of the file.')
    parser.add_argument('diary', type=str, nargs='?',
                        help='Diary filename to use. If not given, read from stdin.')

    args = parser.parse_args()

    if args.diary:
        instream = open(args.diary, 'r')
    else:
        if args.verbose:
            print('No file given, reading from stdin.')
        instream = sys.stdin

    firstDT = None
    lastDT = None
    for ii, line in enumerate(instream):
        parts = line.split(None, 1)
        if len(parts) == 1:
            timestamp, rest = parts[0], ''
        else:
            timestamp, rest = parts

        try:
            ints = [int(st) for st in timestamp.split('.')]
            ints[-1] *= 1000   # Convert milliseconds to microseconds
            thisDT = datetime(*ints)
        except Exception as ee:
            #print(traceback.format_exc())
            #print('Error with line %d: "%s"' % (ii, line[:-1] if line[-1] == '\n' else line))
            #sys.exit(1)
            # Couldn't parse timestamp, so this is probably a line without timestamp. Just print it.
            print('%9s   %s   %s' % ('', timestamp, rest))            
        else:
            if firstDT is None:
                firstDT = thisDT
                lastDT = thisDT
            delta = thisDT - firstDT if args.total else thisDT - lastDT
            deltaSeconds = delta.days * 3600 * 24 + delta.seconds + delta.microseconds / 1e6
            if len(rest) > 0 and rest[-1] == '\n':
                rest = rest[:-1]

            deltaSecondsString = '+' + '%.03f' % deltaSeconds
            print('%9s   %s   %s' % (deltaSecondsString, timestamp, rest))

            lastDT = thisDT


if __name__ == '__main__':
    sys.exit(main())
