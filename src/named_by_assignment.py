from dataclasses import dataclass
from typing import Dict
import operator
import sympy
import sympy.stats


class AbstractReal:

    def __add__(self, other):
        return Operation(operator.add, (self, other))
    
    def __mul__(self, other):
        return Operation(operator.mul, (self, other))
    
    def __pow__(self, other):
        return Operation(operator.pow, (self, other))


@dataclass
class Operation(AbstractReal):
    operator: callable
    operands: tuple
    

@dataclass
class AsYetUnnamed(AbstractReal):
    constructor: callable
    args: tuple
    kwargs: Dict[str, object]
    

@dataclass
class NamedByAssignment:
    constructor: callable
        
    def __call__(self, *args, **kwargs):
        return AsYetUnnamed(self.constructor, args, kwargs)


class DictStruct:
    def __init__(self, **contents):
        self.__dict__ = contents


def build_model(env):
    translation = {}
    for name, unnamed in env.items():
        if not isinstance(unnamed, AsYetUnnamed):
            continue
        translation[id(unnamed)] = unnamed.constructor(name, *unnamed.args, **unnamed.kwargs)
    def convert(x):
        key = id(x)
        if key in translation:
            return translation[key]
        if isinstance(x, Operation):
            x = x.operator(*map(convert, x.operands))
        # otherwise x is a constant and needs no conversion.
        translation[key] = x
        return x
    for x in env.values():
        convert(x)

    model = {name: translation[id(v)] for (name,v) in env.items()
             if (id(v) in translation) and isinstance(v, (AsYetUnnamed, Operation))
            }
    return DictStruct(**model)


Normal = NamedByAssignment(sympy.stats.Normal)
def sin(r): return Operation(sympy.sin, (r,)) 
def cos(r): return Operation(sympy.cos, (r,))


def test():
    from sympy.stats import sample
    x = Normal(0,1)
    y = x*x
    one = sin(x) ** 2 + cos(x) ** 2
    model = build_model(locals())
    print("roughly 0:", sample(model.x, size=10000).mean())
    print("roughly 1:", sample(model.y, size=10000).mean())
    print("exactly 1s:", sample(model.one, size=10))

