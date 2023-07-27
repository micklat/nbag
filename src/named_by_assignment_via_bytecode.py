import sys, dis

def assignee_name(frame=None):
    if frame is None:
        frame = sys._getframe(2)
    caller_code = frame.f_code
    lines = {line: (start,end) for (start,end,line) in caller_code.co_lines()}
    instructions = list(dis.get_instructions(caller_code))
    line_starters = {inst.starts_line:i for (i,inst) in enumerate(instructions) if inst.starts_line is not None}
    caller_line = frame.f_lineno
    next_line = min([li for li in line_starters if li > frame.f_lineno])
    assignment = instructions[line_starters[caller_line]: line_starters[next_line]]
    assert assignment[-2].opname=="CALL_FUNCTION"
    assert assignment[-1].opname=="STORE_FAST"
    return assignment[-1].argval

import sympy.stats

def normal(mean, std):
    return sympy.stats.Normal(assignee_name(), mean, std)

def x_squared():
    x = normal(0, 2)
    return x*x
    
import sympy
print(sympy.stats.sample(x_squared(), size=1000000).mean())
