from time import sleep
from hm_pyhelper.lock_singleton import LockSingleton, \
    ResourceBusyError, CannotLockError

lock = LockSingleton("resource1")

try:
    # try to acquire the resource or may raise an exception
    lock.acquire()

    # do some work
    sleep(5)

    # release the resource
    lock.release()
except ResourceBusyError:
    print("The resource is busy now.")
except CannotLockError:
    print("Can't lock the resource for some internal issue.")
