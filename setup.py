#! /usr/bin/env python

from distutils.core import setup

with open('README') as ff:
    long_description = ff.read()
url='https://github.com/yosinski/GitResultsManager'

setup(name='GitResultsManager',
      description='The GitResultsManager Python module and scripts (resman) for keeping track of research results using Git.',
      long_description=long_description,
      version='0.2',
      url=url,
      author='Jason Yosinski',
      author_email='git_results_manager.jyo@0sg.net',
      py_modules=['GitResultsManager'],
      )


print
print '*' * 70
print '''*  Note: GitResultsManager comes with several very useful scripts'''
print '''*  (resman, resman-td, git-recreate) which are not installed by'''
print '''*    pip install GitResultsManager'''
print '''*  To install these scripts, simply run the one line command from:'''
print '''*    %s''' % url
print '*' * 70
print
