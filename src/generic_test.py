from named_by_assignment import GenericWrapper
import sympy
import sympy.stats

Normal = GenericWrapper(sympy.stats.Normal)


def cost():
    setup_cost = Normal(3,1)
    operation_cost = 1000
    return setup_cost + operation_cost

def benefit():
    x = Normal(0,1)
    return 1 + x ** 2

def test():
    from sympy.stats import sample
    x = Normal(0,1)
    y = x*x
    one = sin(x) ** 2 + cos(x) ** 2
    ratio = cost() / benefit()
    assert sample(ratio) > 0
    print("roughly 0:", sample(x, size=1000000).mean())
    print("roughly 1:", sample(y, size=1000000).mean())
    print("exactly 1s:", sample(one, size=10))

