from dataclasses import dataclass
from typing import Callable
import dis, sys, opcode


def assignee_name(depth=2) -> str:
    frame = sys._getframe(depth)
    for inst in dis.get_instructions(frame.f_code):
        if inst.offset > frame.f_lasti:
            if opcode.opname[inst.opcode] in ("STORE_FAST", "STORE_GLOBAL", "STORE_NAME", "STORE_ATTR"):
                return inst.argval
            break 
    callee = sys._getframe(depth-1).f_code.co_name
    raise Exception(callee + f" should be called as the right-hand-side of an assignment statement, e.g.: x = {callee}(args...)")


@dataclass
class GenericWrapper:
    constructor: Callable
        
    def __call__(self, *args, **kwargs):
        name = assignee_name(2)
        return self.constructor(name, *args, **kwargs)
    

