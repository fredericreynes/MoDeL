from __future__ import print_function

enabled = True

def log(*args):
    if enabled:
        print(*args)
