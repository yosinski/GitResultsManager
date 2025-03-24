#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import select
import signal
import argparse
import subprocess
from GitResultsManager import GitResultsManager, makeAsync, readAsync


def main():
    parser = argparse.ArgumentParser(description='resman is a wrapper script to log output from a given command and capture useful git status. For more information, see https://github.com/yosinski/GitResultsManager. Note: if you are trying to use resman to run commands with options, like "resman -r test1 mycommand --foo --bar", separate your command and options from resman by inserting -- like so: "resman -r test1 -- command --foo --bar".',
                                     formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog))
    parser.add_argument('--runname', '-r', type=str, default='junk',
                        help='Name for GitResultsManager results directory')
    parser.add_argument('--dirname', '-d', type=str, default='results',
                        help='Directory in which to create timestamped results directories')
    parser.add_argument('--nodiary', '-n', action='store_true',
                        help='Disable diary')
    parser.add_argument('--nomkdir', action='store_true',
                        help='If the "results" directory (or the name specified by --dirname) does not exist, resman will create it unless the --nomkdir option is selected. With this option, resman wil instead raise an exception if the "results" directory is missing')
    parser.add_argument('--template', '-t', type=str, default=None,
                        help='Template to use for the name of the created results directory, in Python string format notation. Available keys are "date", "time", "dt" (date_time), "githash", "gitbranch", and "runname". Keys may be omitted. The default template is "{dt}_{githash}_{gitbranch}_{runname}", which may be overridden by passing a new value using this argument or by setting the environment variable GIT_RESULTS_MANAGER_TEMPLATE. If both are defined, the command line argument takes precedence.')
    parser.add_argument('command', type=str, nargs='+',
                        help='Command to run and all associated args')

    args = parser.parse_args()
    if args.template is None:
        args.template = os.environ.get('GIT_RESULTS_MANAGER_TEMPLATE', '{dt}_{githash}_{gitbranch}_{runname}')

    gitresman = GitResultsManager(resultsSubdir=args.dirname)
    gitresman.start(args.template,
                    args.runname,
                    diary=not args.nodiary,
                    createResultsDirIfMissing=not args.nomkdir)

    print(' Raw script command:', ' '.join(args.command))
    args.command = [item.replace('GIT_RESULTS_MANAGER_DIR', gitresman.rundir) for item in args.command]
    print('     Script command:', ' '.join(args.command))

    os.environ['GIT_RESULTS_MANAGER_DIR'] = gitresman.rundir
    print()
    # JBY: using universal_newlines=True in py3 proved not to work directly because of this bug or change:
    #  https://bugs.python.org/issue35762
    #proc = subprocess.Popen(args.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    proc = subprocess.Popen(args.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    makeAsync(proc.stdout)
    makeAsync(proc.stderr)

    while True:
        try:
            # Wait for data to become available
            select.select([proc.stdout, proc.stderr], [], [])
        except KeyboardInterrupt:
            # Catch Ctrl+C, pass to child, and continue
            proc.send_signal(signal.SIGINT)

        # Try reading some data from each
        stdoutBlob = readAsync(proc.stdout)
        stderrBlob = readAsync(proc.stderr)

        if stdoutBlob:
            print(stdoutBlob, end='')
        if stderrBlob:
            print(stderrBlob, end='', file=sys.stderr)

        exitCode = proc.poll()
        if exitCode != None:
            # TODO: read last stdout/stderr here? Ok to use blocking read?
            break

    print()
    print('       Exit code: ', exitCode)

    gitresman.stop(procTime=False)

    return exitCode


if __name__ == '__main__':
    sys.exit(main())
