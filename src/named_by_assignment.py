from dataclasses import dataclass
from collections.abc import Mapping, Iterable, Callable
from abc import ABC, abstractmethod 
from typing import Dict
import sys
import operator
import sympy
import sympy.stats


class AbstractReal(ABC):

    def __add__(self, other):
        return Operation(operator.add, (self, other))
    
    def __radd__(self, other):
        return Operation(operator.add, (other, self))

    def __mul__(self, other):
        return Operation(operator.mul, (self, other))
    
    def __pow__(self, other):
        return Operation(operator.pow, (self, other))

    def __truediv__(self, other):
        return Operation(operator.truediv, (self, other))


class Resolvable(ABC):
    @abstractmethod
    def resolve(self):
        ...

def resolve(x):
    return x.resolve() if isinstance(x, Resolvable) else x


class Missing():
    pass
_missing = Missing()


@dataclass
class Operation(AbstractReal, Resolvable):
    operator: Callable
    operands: tuple
    resolved: object = _missing

    def resolve(self):
        if self.resolved is _missing:
            self.resolved = self.operator(*map(resolve, self.operands))
        return self.resolved


@dataclass
class AutoNamed(AbstractReal, Resolvable):
    constructor: Callable
    args: tuple
    kwargs: Dict[str, object]
    definition_context: Dict[str, object]
    resolved: object = _missing

    def resolve(self):
        if self.resolved is _missing:
            matches = [k for k,v in self.definition_context.items() if v is self]
            if not matches:
                raise Exception("no name specified by assignment", self)
            name = matches[0]
            self.resolved = self.constructor(
                    name, *map(resolve, self.args), **generalized_map(resolve, self.kwargs))
            self.definition_context = None
        return self.resolved


@dataclass
class Wrapper:
    constructor: Callable
        
    def __call__(self, *args, **kwargs):
        context = sys._getframe(1).f_locals
        return AutoNamed(self.constructor, args, kwargs, context)
    

class DictStruct:
    def __init__(self, **contents):
        self.__dict__ = contents


def generalized_map(f, x, *args, **kwargs):
    if isinstance(x, Mapping):
        return {name: f(v, *args, **kwargs) for (name,v) in x.items()}
    if isinstance(x, Iterable):
        return [f(v, *args, **kwargs) for v in x]
    return f(x, *args, **kwargs)


def model(env=_missing):
    if env is _missing:
        env = sys._getframe(1).f_locals
        env = {k:v for k,v in env.items() if isinstance(v, (Resolvable, sympy.Basic))}
    result = generalized_map(resolve, env)
    if isinstance(result, dict):
        return DictStruct(**result)
    return result


Normal = Wrapper(sympy.stats.Normal)
def sin(r): return Operation(sympy.sin, (r,)) 
def cos(r): return Operation(sympy.cos, (r,))


def cost():
    capital_cost = Normal(3,1)
    operation_cost = 1000
    total = capital_cost + operation_cost
    return model()

def benefit():
    x = Normal(0,1)
    total = 1 + x ** 2
    return model()

def test():
    from sympy.stats import sample
    x = Normal(0,1)
    y = x*x
    one = sin(x) ** 2 + cos(x) ** 2
    ratio = cost().total / benefit().total
    m = model()
    assert sample(m.ratio) > 0
    print("roughly 0:", sample(m.x, size=10000).mean())
    print("roughly 1:", sample(m.y, size=10000).mean())
    print("exactly 1s:", sample(m.one, size=10))

