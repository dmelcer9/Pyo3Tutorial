from concurrent.futures import ThreadPoolExecutor
from time import sleep
from timeit import timeit

from simple_pyo3.native import fib as fib_native
from simple_pyo3.native import fib_detached as fib_native_detached

def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

def map_and_join(ex: ThreadPoolExecutor, fun):
    inputs = [35] * 4
    val = ex.map(fun, inputs)
    return list(val)




if __name__ == '__main__':
    print("Python (single-thread): " + str(timeit(lambda: fib(35), number=1)))
    print("Rust   (single-thread): " + str(timeit(lambda: fib_native(35), number=1)))

    with ThreadPoolExecutor(max_workers=4) as executor:
        print("Python (multi-thread):  " + str(timeit(lambda: map_and_join(executor, fib), number=1)))
        print("Rust   (multi-thread):  " + str(timeit(lambda: map_and_join(executor, fib_native), number=1)))

        sleep(0.1)  # So the warning printing doesn't get clobbered
        # noinspection PyUnusedImports
        import msgpack  # Contains a native extension module that doesn't support GIL
        sleep(0.1)

        print("Python (multi, gil):    " + str(timeit(lambda: map_and_join(executor, fib), number=1)))
        print("Rust   (multi, gil):    " + str(timeit(lambda: map_and_join(executor, fib_native), number=1)))
        print("Rust-d (multi, gil):    " + str(timeit(lambda: map_and_join(executor, fib_native_detached), number=1)))
