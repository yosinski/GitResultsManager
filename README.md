GitResultsManager
=====================



Installing
---------------------

```
pip install GitResultsManager
```

Using a [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) is recommended.



Usage
---------------------

GitResultsManager may be used in two ways:

1. Using the `resman` wrapper script to run programs in any language. This is the simplest way of using GitResultsManager to track results and plays well with programs in Python or any other language.
2. From within Python as a Python module.

(1) is more general, while (2) offers more control. The following examples are available in the `examples` directory.



### Simple example: use `resman` wrapper script to run a program

Let's run something simple without GitResultsManager:

    $ echo Hello World
    Hello World

Now, let's run it with `resman`:

```
$ resman echo Hello World
WARNING: GitResultsManager running in GIT_DISABLED mode: no git information saved! (Is /Users/jason in a git repo?)
  Logging directory: results/250324_160729_nogithash_junk
 Raw entire command: /Users/jason/virtualenvs/default/bin/resman echo Hello World
           Hostname: lapaz
  Working directory: /Users/jason
 Raw script command: echo Hello World
     Script command: echo Hello World

Hello World

       Exit code:  0
       Wall time:  0.227
```

Notice how `resman` adds a few lines of information to the beginning and ending of the output? Looking at each line in order:

    WARNING: GitResultsManager running in GIT_DISABLED mode: no git information saved! (Is /Users/jason in a git repo?)

Warning because we aren't running from within a git repository, removing most of the usefulness of GitResultsManager.

      Logging directory: results/250324_160729_nogithash_junk

The directory that was created for this run, in the format `<datestamp>_<timestamp>_<githash>_<name of run>`. We did not run from within a git repo, so instead of a git hash, the results dir contains `nogithash`. We also did not specify a run name, so `resman` uses `junk` by default. A common development pattern is to run and re-run code, debugging as needed and logging to directories ending in `junk`. When the code is ready for a real, often longer and more serious run, re-run using the `--runname` argument to specify the more permanent name of the run.

         Script command: echo Hello World

Which command you actually ran.

               Hostname: lapaz

The host this run was performed on (useful when running on clusters or
multiple machines with non-identical configurations)

      Working directory: /Users/jason

The working directory. Next follows the actual output of the program, and then at the end...

           Exit code:  0
           Wall time:  0.227

`resman` notes the exit code and how long the program took to execute in wall time.



### Example of using `resman` wrapper script to run a C program:

First, we'll compile the `demo-c` program (from the examples directory) and run it without `resman`:

    $ g++ -o demo-c demo-c.cc   # compile program first if necessary
    $ ./demo-c

Output:

    Environment variable GIT_RESULTS_MANAGER_DIR is undefined. To demonstrate logging, run this instead as
        resman ./demo-c
    This line is logged
    This line is logged (stderr)
    This line is logged
    This line is logged (stderr)
    This line is logged
    This line is logged (stderr)

Notice that it complains it cannot find the GIT_RESULTS_MANAGER_DIR
environment variable. This is how the program knows it is not being
run from within `resman`. Now, try using `resman` to run it:

    $ resman -r run-name ./demo-c

Output:

      Logging directory: results/250324_161817_a8fe279_run-name
     Raw entire command: /Users/jason/virtualenvs/default/bin/resman -r run-name ./demo-c
               Hostname: lapaz
      Working directory: /Users/jason/s/GitResultsManager/examples
     Raw script command: ./demo-c
         Script command: ./demo-c
    
    The current GIT_RESULTS_MANAGER_DIR is: results/250324_161817_a8fe279_run-name
    This line is logged
    This line is logged
    This line is logged
    This line is logged (stderr)
    This line is logged (stderr)
    This line is logged (stderr)
    
           Exit code:  0
           Wall time:  0.238

As earlier, `resman` adds logging info, and this time the program can access the directory created by `resman` for it. Here the program just prints this info, but in theory it could save plots, data files, etc to that directory. Note that several of the lines are re-ordered; this is due to the OS separately buffering stdout and stderr. In general, print statements are correctly ordered if they are all written to stdout or all to stderr.



### Simple code change to use `resman` wrapper script in Python:

Import the `os` module:

    import os

Check if we're running from within `resman`. If so, use the directory `resman` provides, else save output to the current directory:

    try:
        savedir = os.environ['GIT_RESULTS_MANAGER_DIR']
    except KeyError:
        savedir = '.'
    
    # later in code, when saving plots / etc:
    
    savefig(os.path.join(savedir, 'myplot.png'))



### Example of using the `GitResultsManager` class within Python.

See `examples/demo-GRM-module.py`. This approach is only needed if one wants more control of GitResultsManager directly from within Python. For example, one could use it to run a for loop of many hyperparameters and log each to separate directories.





Platform requirements
----------------------

GitResultsManager has been tested on Linux and Mac. Evidence of success on other OSs is appreciated.





Development task list
----------------------

### To do

1. Add settings override via `~/.config/gitresultsmanager_config.py` or similar
1. Documentation

Want to help? Pull requests are welcome!
