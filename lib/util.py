#
#
#   Util
#   This module contains many functions and objects reused throughout the software
#
#
import sys
from collections import deque

#   Error
#   Print Error Message to Screen
#
#   message - message to print to screen
#   do_exit - if set, error will end program. Defaults to False
def error(message, do_exit=False):
    message = "ERROR " + message
    if do_exit:
        sys.exit(message)
    else:
        print(message)


#   Load File
#   Pull in processes from text records into memory
#
#   message - message to print to screen
#   do_exit - if set, error will end program. Defaults to False
def load_file(file):
    list = []

    for line in file.readlines():
        line.replace("\n", "")

        tokens = [line.strip() for line in line.split(',')]

        if len(tokens) == 2:
            list.append([
                int(tokens[0]),
                int(tokens[1]),
            ])

    return list


def deepcopy(arr):
    return [row[:] for row in arr]