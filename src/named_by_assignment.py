from dataclasses import dataclass


def assignee_name(frame=2):
    import sys, dis
    if isinstance(frame, int): frame = sys._getframe(frame)
    elif frame is None: frame = sys._getframe(2)
    for inst in dis.get_instructions(frame.f_code):
        if inst.offset > frame.f_lasti:
            assert opcode.opname[inst.opcode] in ("STORE_FAST", "STORE_GLOBAL", "STORE_NAME", "STORE_ATTR")            
            return inst.argval
    raise Exception("this function should be called as the right-hand-side of an assignment statement")


@dataclass
class GenericWrapper:
    constructor: Callable
        
    def __call__(self, *args, **kwargs):
        name = assignee_name(2)
        return self.constructor(name, args, kwargs)
    

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
    print("roughly 0:", sample(x, size=10000).mean())
    print("roughly 1:", sample(y, size=10000).mean())
    print("exactly 1s:", sample(one, size=10))

