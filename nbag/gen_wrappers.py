from inspect import Signature, Parameter
import inspect
import sys, os.path
from functools import reduce
from dataclasses import dataclass
from typing import Callable, Optional
from importlib import import_module


def try_signature(f: Callable) -> Optional[Signature]:
    try:
        return inspect.signature(f)
    except (ValueError, TypeError):
        return None


def should_wrap(s: Signature) -> bool:
    params = s.parameters
    if not params: return False
    p0 = next(iter(s.parameters.values()))
    if p0.name != "name": return False
    return (p0.annotation is p0.empty) or (p0.annotation is str)


@dataclass
class ArgsGenerator:
    parameters: list[Parameter]

    def declared_args(self, new_kw_args=[]):
        po_args = []
        pok_args = []
        kwo_args = []
        any_star = False
        any_kw_only = False
        for p in self.parameters:
            s = ""
            if p.kind == p.POSITIONAL_ONLY:
                args = po_args
            elif p.kind == p.POSITIONAL_OR_KEYWORD:
                args = pok_args
            elif p.kind == p.VAR_POSITIONAL:
                args = po_args
                s += '*'
                any_star = True
            elif p.kind == p.KEYWORD_ONLY:
                args = kwo_args
                any_kw_only = True
            elif p.kind == p.VAR_KEYWORD:
                s += '**'
                args = kwo_args
            else:
                assert False, "unexpected parameter kind: "+repr(p)

            s += p.name
            if p.annotation is not inspect._empty:
                s += ':' + str(p.annotation)
            if p.default is not inspect._empty:
                s += '=' + repr(p.default)
            args.append(s) 

        slashes = ["/"] if po_args else []
        stars = ["*"] if (any_kw_only and not any_star) else []
        return ', '.join(po_args + slashes + pok_args + new_kw_args + stars + kwo_args)

    def pass_positionals(self):
        positional = []
        for p in self.parameters:
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
                positional.append(p.name)
                continue
            if p.kind==p.VAR_POSITIONAL:
                positional.append(f"*{p.name}")
                break
            assert p.kind in (p.VAR_KEYWORD, p.KEYWORD_ONLY)
            break
        return positional
        
    def pass_kw(self):
        bindings = []
        for p in self.parameters:
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL):
                continue
            if p.kind == p.KEYWORD_ONLY:
                bindings.append(f"{p.name}={p.name}")
                continue
            if p.kind == p.VAR_KEYWORD:
                bindings.append(f"**{p.name}")
                continue
            assert False
        return bindings 

   
@dataclass
class WrapperCode:
    wrapped_name: str
    wrapper_name: str
    imports: list[str]
    definition: str

def wrap_function(f: Callable, module_path: str, lower_name: bool):
    s = try_signature(f)
    if not (s and should_wrap(s)): return None
    qualified_f_name = module_path + "." + f.__name__
    params = list(s.parameters.values())[1:] # skip the first parameter which is assumed to be "name"
    args = ArgsGenerator(params)
    imports = [module_path]
    wrapper_formal_args = args.declared_args(["name=None"])
    construct_args = ', '.join([qualified_f_name, "name"] + args.pass_positionals() + args.pass_kw())
    wrapper_name = f.__name__
    if lower_name:
        wrapper_name = wrapper_name[0].lower() + wrapper_name[1:]
    definition = (
            f"def {wrapper_name}({wrapper_formal_args}):\n"
            +f"    return construct({construct_args})\n"
            )
    return WrapperCode(f.__name__, wrapper_name, imports, definition)

def wrap_module_functions(module, dest, names=None, lower_names=True):
    module_path = module.__name__
    if names is None:
        names = [name for name in dir(module) if not name.startswith('_')]

    objects = {name: getattr(module, name) for name in names}
    functions = {name:v for (name,v) in objects.items() if callable(v)}
    wrappers = [wrap_function(v, module_path, lower_names) for v in functions.values()]
    wrappers = [w for w in wrappers if w]

    imports = sorted(reduce(frozenset.union, [w.imports for w in wrappers], frozenset()))
    with open(dest, 'w') as out:
        print(f"from {module_path} import *", file=out)
        print("from nbag import construct", file=out)
        for module in imports:
            print("import "+module, file=out)
        print("\n", file=out)
        for w in wrappers:
            print(w.definition, file=out)


def ensure_package(p: str):
    import os, os.path
    if not os.path.exists(p):
        os.mkdir(p)
    init = os.path.join(p, "__init__.py")
    if not os.path.exists(init):
        with open(init,'w'):
            pass


def ensure_containing_package(p: str):
    prefix = p.rpartition(os.path.sep)[0]
    if prefix:
        ensure_containing_package(prefix)
        ensure_package(prefix)


def ispackage(m):
    return m.__package__ == m.__name__


PACKAGE_PREFIX = "nba_" # short for "named by assignment"

def wrap_module(module_name: str, dest_dir: str) -> None:
    module = import_module(module_name)
    wrapped_package = module_name.split('.')[0] # e.g. "sympy"
    wrapper_package = PACKAGE_PREFIX + wrapped_package # e.g. "nba_sympy"
    wrapper_path = os.path.join(dest_dir, *(PACKAGE_PREFIX + module_name).split('.'))
    if ispackage(module):
        wrapper_path += os.path.sep + "__init__.py"
    else:
        wrapper_path += ".py"
    ensure_containing_package(wrapper_path)
    wrap_module_functions(module, wrapper_path)
    

