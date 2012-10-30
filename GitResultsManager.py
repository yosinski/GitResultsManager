#! /usr/bin/env python

import os
import sys
import logging
import stat
import subprocess
import datetime
import time
import pdb



def fmtSeconds(sec):
    sign = ''
    if sec < 0:
        sign = '-'
        sec = -sec
    hours, remainder = divmod(sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return sign + '%d:%02d:%02d' % (hours, minutes, int(seconds)) + ('%.3f' % (seconds-int(seconds)))[1:]
    elif minutes > 0:
        return sign + '%d:%02d' % (minutes, int(seconds)) + ('%.3f' % (seconds-int(seconds)))[1:]
    else:
        return sign + '%d' % int(seconds) + ('%.3f' % (seconds-int(seconds)))[1:]



class OutstreamHandler(object):
    def __init__(self, writeHandler, flushHandler):
        self.writeHandler = writeHandler
        self.flushHandler = flushHandler

    def write(self, message):
        self.writeHandler(message)

    def flush(self):
        self.flushHandler()



class OutputLogger(object):
    '''A logging utility to override sys.stdout'''

    '''Buffer states'''
    class BState:
        EMPTY  = 0
        STDOUT = 1
        STDERR = 2
            
    def __init__(self, filename):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.log = logging.getLogger('autologger')
        self.log.propagate = False
        self.log.setLevel(logging.DEBUG)
        self.fileHandler = logging.FileHandler(filename)
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(message)s', datefmt='%y.%m.%d.%H.%M.%S')
        self.fileHandler.setFormatter(formatter)
        self.log.addHandler(self.fileHandler)

        self.stdOutHandler = OutstreamHandler(self.handleWriteOut,
                                              self.handleFlushOut)
        self.stdErrHandler = OutstreamHandler(self.handleWriteErr,
                                              self.handleFlushErr)
        self.buffer = ''
        self.bufferState = self.BState.EMPTY
        self.started = False


    def startCapture(self):
        if self.started:
            raise Exception('ERROR: OutputLogger capture was already started.')
        self.started = True
        sys.stdout = self.stdOutHandler
        sys.stderr = self.stdErrHandler

    def finishCapture(self):
        if not self.started:
            raise Exception('ERROR: OutputLogger capture was not started.')
        self.started = False
        self.flush()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def handleWriteOut(self, message):
        self.write(message, self.BState.STDOUT)
        
    def handleWriteErr(self, message):
        self.write(message, self.BState.STDERR)

    def handleFlushOut(self):
        self.flush()
        
    def handleFlushErr(self):
        self.flush()
        
    def write(self, message, destination):
        if destination == self.BState.STDOUT:
            self.stdout.write(message)
        else:
            self.stderr.write(message)
        
        if destination == self.bufferState or self.bufferState == self.BState.EMPTY:
            self.buffer += message
            self.bufferState = destination
        else:
            # flush and change buffer
            self.flush()
            assert(self.buffer == '')
            self.bufferState = destination
            self.buffer = '' + message
        if '\n' in self.buffer:
            self.flush()

    def flush(self):
        self.stdout.flush()
        self.stderr.flush()
        if self.bufferState != self.BState.EMPTY:
            if len(self.buffer) > 0 and self.buffer[-1] == '\n':
                self.buffer = self.buffer[:-1]
            if self.bufferState == self.BState.STDOUT:
                for line in self.buffer.split('\n'):
                    self.log.info('  ' + line)
            elif self.bufferState == self.BState.STDERR:
                for line in self.buffer.split('\n'):
                    self.log.info('* ' + line)
            self.buffer = ''
            self.bufferState = self.BState.EMPTY
        self.fileHandler.flush()



def runCmd(args, supressErr = False):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = proc.communicate()
    code = proc.wait()

    if code != 0 and not supressErr:
        print out
        print err
        raise Exception('Got error from running command with args ' + repr(args))

    return code, out, err



def gitWorks():
    code,out,err = runCmd(('git','status'), supressErr = True)
    return code == 0



def gitLastCommit():
    return runCmd(('git', 'rev-parse', '--short', 'HEAD'))[1].strip()



def gitCurrentBranch():
    code, out, err = runCmd(('git', 'branch'))
    for line in out.split('\n'):
        if len(line) > 2 and line[0] == '*':
            return line[2:]
    raise Exception('Error getting current branch from git stdout/stderr %s, %s.' % (repr(out), repr(err)))



def gitStatus():
    return runCmd(('git', 'status'))[1].strip()



def gitDiff(color = False):
    if color:
        return runCmd(('git', 'diff', '--color'))[1].strip()
    else:
        return runCmd(('git', 'diff'))[1].strip()



def hostname():
    return runCmd('hostname')[1].strip()



def env():
    return runCmd('env')[1].strip()



RESULTS_SUBDIR = 'results'

class GitResultsManager(object):
    '''Creates directory for results. If created with
    resumeExistingRun, load info from that run, usually just so the
    run can be finished and the diary properly terminated.'''

    def __init__(self, resultsSubdir = None, resumeExistingRun = None):
        self._resumeExistingRun = resumeExistingRun
        if self._resumeExistingRun:
            # if user provided a directory to load in.
            try:
                dirExists = stat.S_ISDIR(os.stat(self._resumeExistingRun).st_mode)
            except OSError:
                pass
            if not dirExists:
                raise Exception('Tried to resume run from "%s", but it is not a results directory', self._resumeExistingRun)

            with open(os.path.join(self._resumeExistingRun, 'diary'), 'r') as diaryFile:
                firstLine = diaryFile.next()
            ints = [int(xx) for xx in firstLine.split()[0].split('.')]
            year,month,day,hour,minute,second,ms = ints

            startWallDt = datetime.datetime(year + 2000, month, day, hour, minute, second, ms * 1000)
            self.startWall = time.mktime(startWallDt.timetuple())
            self.startProc = None
            self.diary = False   # External run, so it's not a diary we're managing

            print 'grabbed time:', self.startWall

        else:
            self._resultsSubdir = resultsSubdir
            if self._resultsSubdir is None:
                self._resultsSubdir = RESULTS_SUBDIR
            self._name = None
            self._outLogger = None
            self.diary = None
        
    def start(self, description = '', diary = True):
        dirExists = False
        try:
            dirExists = stat.S_ISDIR(os.stat(self._resultsSubdir).st_mode)
        except OSError:
            pass
        if not dirExists:
            raise Exception('Please create the results directory "%s" first.' % self._resultsSubdir)

        if ' ' in description:
            raise Exception('Description must not contain any spaces, but it is "%s"' % description)

        if self._name is not None:
            self.finish()
        self.diary = diary

        # Test git
        useGit = gitWorks()

        timestamp = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        if useGit:
            lastCommit = gitLastCommit()
            curBranch = gitCurrentBranch()
            basename = '%s_%s_%s' % (timestamp, lastCommit, curBranch)
        else:
            basename = '%s' % timestamp

        if description:
            basename += '_%s' % description
        success = False
        ii = 0
        while not success:
            name = basename + ('_%d' % ii if ii > 0 else '')
            try:
                os.mkdir(os.path.join(self._resultsSubdir, name))
                success = True
            except OSError:
                print >>sys.stderr, name, 'already exists, appending suffix to name'
                ii += 1
        self._name = name

        if self.diary:
            self._outLogger = OutputLogger(os.path.join(self.rundir, 'diary'))
            self._outLogger.startCapture()

        self.startWall = time.time()
        self.startProc = time.clock()

        # TODO: remove redundancy
        # print the command that was executed
        print >>sys.stderr, 'WARNING: GitResultsManager running in GIT_DISABLED mode! (Is this a git repo?)'
        print '  Logging directory:', self.rundir
        print '        Command run:', ' '.join(sys.argv)
        print '           Hostname:', hostname()
        print '  Working directory:', os.getcwd()
        if not self.diary:
            print '<diary not saved>'
            # just log these three lines
            with open(os.path.join(self.rundir, 'diary'), 'w') as ff:
                print >>ff, 'WARNING: GitResultsManager running in GIT_DISABLED mode! (Is this a git repo?)'
                print >>ff, '  Logging directory:', self.rundir
                print >>ff, '        Command run:', ' '.join(sys.argv)
                print >>ff, '           Hostname:', hostname()
                print >>ff, '  Working directory:', os.getcwd()
                print >>ff, '<diary not saved>'

        if useGit:
            with open(os.path.join(self.rundir, 'gitinfo'), 'w') as ff:
                ff.write('%s %s\n' % (lastCommit, curBranch))
            with open(os.path.join(self.rundir, 'gitstat'), 'w') as ff:
                ff.write(gitStatus() + '\n')
            with open(os.path.join(self.rundir, 'gitdiff'), 'w') as ff:
                ff.write(gitDiff() + '\n')
            with open(os.path.join(self.rundir, 'gitcolordiff'), 'w') as ff:
                ff.write(gitDiff(color=True) + '\n')
        with open(os.path.join(self.rundir, 'env'), 'w') as ff:
            ff.write(env() + '\n')

    def stop(self):
        if self._resumeExistingRun:
            procTimeSec = '<unknown, not managed by GitResultsManager>'
        else:
            procTimeSec = fmtSeconds(time.clock() - self.startProc)
        if not self.diary:
            # just log these couple lines before resetting our name
            with open(os.path.join(self.rundir, 'diary'), 'a') as ff:
                print >>ff, '       Wall time: ', fmtSeconds(time.time() - self.startWall)
                print >>ff, '  Processor time: ', procTimeSec
        self._name = None
        print '       Wall time: ', fmtSeconds(time.time() - self.startWall)
        print '  Processor time: ', procTimeSec
        if self.diary:
            self._outLogger.finishCapture()
            self._outLogger = None


    @property
    def rundir(self):
        if self._resumeExistingRun:
            return self._resumeExistingRun
        elif self._name:
            return os.path.join(self._resultsSubdir, self._name)

    @property
    def runname(self):
        if self._resumeExistingRun:
            raise Exception('Not Implemented: Name not defined when runs are resumed.')
        return self._name



# Instantiate a global GitResultsManager for others to use
resman = GitResultsManager()



if __name__ == '__main__':
    print 'This is just a simple demo. See the examples directory in the GitResultsManager distribution for more detailed examples.'

    resman.start()
    print 'this is being logged to the %s directory' % resman.rundir
    time.sleep(1)
    print 'this is being logged to the %s directory' % resman.rundir
    time.sleep(1)
    print 'this is being logged to the %s directory' % resman.rundir
    resman.stop()
