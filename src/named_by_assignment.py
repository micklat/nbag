from dataclasses import dataclass
from typing import Callable
import dis, sys, opcode


def assignee_name(frame=2):
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
        return self.constructor(name, *args, **kwargs)
    

