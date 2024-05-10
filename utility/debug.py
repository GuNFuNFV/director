import sys
import datetime


# define a debug print function
def dprint(*args):
    # print with timestamp, file name, function name, line number, red color and flush
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], sys._getframe(1).f_code.co_filename,
          sys._getframe(1).f_code.co_name, sys._getframe(1).f_lineno, "\033[1;31;40m", *args, "\033[0m", flush=True)


# test debug print function
def test_func():
    dprint("hello test_func")


# test debug print function
def test_func2():
    dprint("hello test_func2")


import inspect

MAX_DEPTH = None


def make_print_depth(max_depth=None):
    # print depth
    def print_depth(message):
        stack_depth = len(inspect.stack()) - 1
        if max_depth is None or stack_depth <= max_depth:
            print(f"{'>' * stack_depth} {message}")

    return print_depth


def Deb(msg=None):
    # current file name and line number
    print(
        f"Debug {sys._getframe().f_back.f_code.co_filename}: {sys._getframe().f_back.f_lineno}: {msg if msg is not None else ''}")


def is_debug():
    import sys

    gettrace = getattr(sys, 'gettrace', None)

    if gettrace is None:
        return False
    else:
        v = gettrace()
        if v is None:
            return False
        else:
            return True


def debug_print(*args):
    # check if the debug mode is on
    if is_debug():
        print(*args)


# execute if this file is run as a script
if __name__ == "__main__":
    test_func()
    test_func2()
