from time import time


class ProgressLogger(object):
    """Loggs the proggress of a process to the passed
    logger.
    """

    def __init__(self, message, iterable, timeout=5):
        self.message = message
        self.iterable = iterable

        if isinstance(iterable, (int, int, float)):
            self.length = iterable
        else:
            self.length = len(iterable)

        self.timeout = timeout
        self._timestamp = None
        self._counter = 0

    def __enter__(self):
        print('Starting %s' % self.message)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            print('Finished %s' % self.message)

        else:
            print('FAILED %s (%s: %s)' % (
                self.message,
                str(exc_type.__name__),
                str(exc_value)))

    def __call__(self):
        self._counter += 1
        if not self.should_be_logged():
            return

        percent = int(self._counter * 100.0 / self.length)
        print('%s of %s (%s%%): %s' % (
            self._counter,
            self.length,
            percent,
            self.message))

    def __iter__(self):
        with self as step:
            for item in self.iterable:
                yield item
                step()

    def should_be_logged(self):
        now = float(time())

        if self._timestamp is None:
            self._timestamp = now
            return True

        next_stamp = self._timestamp + self.timeout
        if next_stamp <= now:
            self._timestamp = now
            return True

        else:
            return False
