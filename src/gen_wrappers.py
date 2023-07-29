from inspect import Signature, Parameter
import sys
import inspect
from functools import reduce
from dataclasses import dataclass
from typing import Callable


def should_wrap(signature: Signature):
    params = signature.parameters
    if not params: return False
    p0 = next(iter(signature.parameters.values()))
    if p0.name != "name": return False
    return ((p0.annotation is p0.empty)
            or (p0.annotation is str))

@dataclass
class ArgsGenerator:
    parameters: list[Parameter]

    def declaration(self):
        args = []
        slash_pending = False
        starred = False
        for p in self.parameters:
            if p.kind==p.POSITIONAL_ONLY:
                slash_pending = True
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
                args.append(f"{p.name}")
                continue
            if slash_pending:
                args.append("/")
            if p.kind==p.VAR_POSITIONAL:
                args.append(f"*{p.name}")
                starred = True
                continue
            if p.kind == p.KEYWORD_ONLY:
                if not starred:
                    args.append("*")
                    starred = True
                args.append(f"{p.name}={repr(p.default)}")
                continue
            if p.kind == p.VAR_KEYWORD:
                args.append(f"**{p.name}")
                continue
            assert False 
        return ", ".join(args)

    def positional_args(self):
        positional = []
        for p in self.parameters:
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
                positional.append(p.name)
                continue
            if p.kind==p.VAR_POSITIONAL:
                if not positional: return p.name
                positional.append(f"*{p.name}")
                break
            assert p.kind in (p.VAR_KEYWORD, p.KEYWORD_ONLY)
            break
        return positional
        
    def kw_args(self):
        bindings = []
        for p in self.parameters:
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL):
                continue
            if p.kind == p.KEYWORD_ONLY:
                bindings.append(f"{repr(p.name)}: {p.name}")
                continue
            if p.kind == p.VAR_KEYWORD:
                bindings.append(f"**{p.name}")
                continue
            assert False
        return bindings 

   
@dataclass
class WrapperCode:
    name: str
    imports: list[str]
    definition: str

def wrap_function(f: Callable, module_path: str):
    s = inspect.signature(f)
    if not should_wrap(s): return None
    qualified_f_name = module_path + "." + f.__name__
    params = list(s.parameters.values())[1:] # skip the first parameter which is assumed to be "name"
    args = ArgsGenerator(params)
    imports = [module_path]
    actuals = ["assignee_name()"] + args.positional_args() + args.kw_args()
    definition = (f"def {f.__name__}({args.declaration()}):\n"
            +f"    return {qualified_f_name}({', '.join(actuals)})\n")
    return WrapperCode(f.__name__, imports, definition)

def wrap_module(module_path, dest, names=None):
    from importlib import import_module
    module = import_module(module_path)
    if names is None:
        names = [name for name in dir(module) if not name.startswith('_')]

    objects = {name: getattr(module, name) for name in names}
    functions = {name:v for (name,v) in objects.items() if callable(v)}
    wrappers = [wrap_function(v, module_path) for v in functions.values()]
    wrappers = [w for w in wrappers if w]

    imports = sorted(reduce(frozenset.union, [w.imports for w in wrappers], frozenset()))
    with open(dest, 'w') as out:
        print("from named_by_assignment import assignee_name", file=out)
        for module in imports:
            print("import "+module, file=out)
        print("\n", file=out)
        for w in wrappers:
            print(w.definition, file=out)


def ensure_module(p: str):
    import os, os.path
    if not os.path.exists(p):
        os.mkdir(p)
    init = os.path.join(p, "__init__.py")
    if not os.path.exists(init):
        with open(init,'w'):
            pass


def wrap_sympy_stats():
    import sympy.stats
    ensure_module("generated")
    ensure_module("generated/sympy")
    wrap_module('sympy.stats', "generated/sympy/stats.py")
    

if __name__ == '__main__':
    wrap_sympy_stats()
