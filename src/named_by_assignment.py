from dataclasses import dataclass
from typing import Callable
import dis, sys, opcode


def assignee_name(depth: int = 2) -> str:
    assert depth>0
    frame = sys._getframe(depth)
    for inst in dis.get_instructions(frame.f_code):
        if inst.offset > frame.f_lasti:
            # TODO: support STORE_ATTR
            if opcode.opname[inst.opcode] in ("STORE_FAST", "STORE_GLOBAL", "STORE_NAME"):
                return inst.argval
            break 
    callee = sys._getframe(depth-1).f_code.co_name
    raise Exception(callee + f" should be called as the right-hand-side of an assignment statement, e.g.: x = {callee}(args...)")


def construct(f, name, *args, **kwargs):
    if name is None:
        name = assignee_name(3)
    return f(name, *args, **kwargs)


@dataclass
class GenericWrapper:
    constructor: Callable
        
    def __call__(self, *args, **kwargs):
        name = assignee_name(2)
        return self.constructor(name, *args, **kwargs)
    

