#! /usr/bin/env python

import sys
import subprocess

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: processwatch.py [command]'

    command = sys.argv[1]
    
    while True:
        subprocess.call(command.split(' '))
