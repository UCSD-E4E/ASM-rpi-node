import signal
from contextlib import contextmanager

@contextmanager
def timeout(time):
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def raise_timeout(signum, frame):
    raise TimeoutError

def func():
    with timeout(1):
        print('enter block')
        import time
        time.sleep(10)
        print('shoundt print')

func()
