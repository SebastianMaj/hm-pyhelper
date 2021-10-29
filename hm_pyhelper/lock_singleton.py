import functools
import os
import posix_ipc
from hm_pyhelper.logger import get_logger

LOGGER = get_logger(__name__)

LOCK_ECC = 'LOCK_ECC'


class LockSingleton(object):
    _prefix = "LockSingleton."
    _mode = 0o644

    def __init__(self, name, initial_value=1):
        self._name = self._prefix + name
        self._initial_value = initial_value
        # so it doesn't interfere with our semaphore mode
        old_umask = os.umask(0)
        try:
            self._sem = posix_ipc.Semaphore(self._name,
                                            mode=self._mode,
                                            flags=posix_ipc.O_CREAT,
                                            initial_value=initial_value)
        finally:
            os.umask(old_umask)

    def acquire(self, timeout=None):
        """Acquire the lock
        """
        try:
            self._sem.acquire(timeout)
        except posix_ipc.BusyError:
            raise ResourceBusyError()
        except posix_ipc.Error:     # Catch all IPC Errors except BusyError
            raise CannotLockError()

        # Consume possible extra semaphore value
        while self._sem.value >= self._initial_value:
            self._sem.acquire(timeout)

    def release(self):
        """Release the lock
        """
        self._sem.release()

    def locked(self):
        return self.value() == 0

    def value(self):
        return self._sem.value


class ResourceBusyError(posix_ipc.Error):
    """
    Raised when a call times out
    """
    def __init__(self, *args, **kwargs):
        pass


class CannotLockError(posix_ipc.Error):
    """
    Raised when can not lock the resource due to the permission issue,
    wrong IPC object or whatever internal issue.
    """
    def __init__(self, *args, **kwargs):
        pass


def ecc_lock(func):
    """Returns an ECC LOCK decorator.
    """
    lock = LockSingleton(LOCK_ECC)

    @functools.wraps(func)
    def wrapper_ecc_lock(*args, **kwargs):
        try:
            # try to acquire the ECC resource or may raise an exception
            lock.acquire()

            value = func(*args, **kwargs)

            # release the resource
            lock.release()

            return value
        except ResourceBusyError:
            LOGGER.error("ECC is busy now.")
        except CannotLockError:
            LOGGER.error("Can't lock the ECC for some internal issue.")

    return wrapper_ecc_lock
