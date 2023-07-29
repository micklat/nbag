from sympy import *
from nba_sympy import *


def test():
    x = symbol()
    y = symbol()
    assert diff(sin(x)*y, x) != x * cos(x)
    assert diff(sin(x)*y, x) == y * cos(x)

if __name__ == "__main__":
    test()

