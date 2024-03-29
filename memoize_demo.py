#!/usr/bin/env python3
import time
import hashlib


class Memoize:
    """ Decorator to keep function resulting data in RAM and save time and used resources on additional function call.
        _expired: Argument given to a decorated function to set how long in seconds to keep the result of the function.
                Default: 0 - keep forever.
    """
    def __init__(self, expired=0):
        self.memo = {}
        self.expired = expired
        self.ts = 0

    def __call__(self, foo):

        def wrapper(*args, **kwargs):
            key = foo.__name__ + '.'.join([str(a) for a in args]) + repr(kwargs)
            key = hashlib.md5(key.encode()).digest()
            # Execute the function if no recorded data found in RAM with given function arguments or if the results expired.
            if not key in self.memo or not self.ts or (self.expired != 0 and time.time() > self.ts + self.expired):
                self.ts = time.time()
                self.memo[key] = foo(*args, **kwargs)
            return self.memo[key]
        return wrapper


# Examples how to use Memoize
# @Memoize(expired=5)
@Memoize()
def long_sleep(secs):
    print('waiting', secs)
    time.sleep(secs)
    print('done')
    return secs


if __name__ == '__main__':

    print(long_sleep(1), time.time())  # takes 1 seconds to run
    print(long_sleep(1), time.time())  # takes nothing :)
    print(long_sleep(10), time.time()) # takes 10 secs
    print(long_sleep(1), time.time())  # takes nothing if 'expired' not set or 1 sec if 'expired' is set <11 in this case
    
