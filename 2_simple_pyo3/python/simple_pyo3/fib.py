from timeit import timeit

from simple_pyo3.native import fib as fib_native

def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)



if __name__ == '__main__':
    print(timeit(lambda: fib(35), number=1))
    print(timeit(lambda: fib_native(35), number=1))
