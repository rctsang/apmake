import os
from pathlib import Path
from typing import Callable, Optional

class Rule:
    """a class to encapsulate a rule"""
    
    def __init__(self, target : str, 
            func : Optional[Callable] = None, 
            reqs : list[str] = [], 
            recurse : bool = False, 
            **kwargs):
        self.target = target
        self.deps = set(reqs)
        self.ders = set()
        self.funcs = {}
        self.recurse = recurse
        if func:
            self.funcs[func] = kwargs

    def __or__(self, other):
        assert self.target == other.target, "cannot merge rules for different targets"
        rule = Rule(target=self.target)
        rule.deps = self.deps | other.deps
        rule.ders = self.ders | other.ders
        # merge must be in order
        for func, kwargs in self.funcs.items():
            rule.funcs[func] = kwargs
        for func, kwargs in other.funcs.items():
            rule.funcs[func] = kwargs
        return rule

    def __ior__(self, other):
        assert self.target == other.target, "cannot merge rules for different targets"
        self.deps |= other.deps
        self.ders |= other.ders
        # merge must be in-order.
        for func, kwargs in other.funcs.items():
            self.funcs[func] = kwargs
        return self

    def __call__(self):
        for func, kwargs in self.funcs.items():
            func(**kwargs)

    def __gt__(self, othr):
        """self > othr if self's target modification time > othr's modification time
        if self's target does not exist return True
        if othr's target does not exist return False
        """
        p_self_target = Path(self.target)
        p_othr_target = Path(othr.target)

        if not p_self_target.exists():
            return True
        elif not p_othr_target.exists():
            return False
        
        return p_self_target.stat().st_mtime > p_othr_target.stat().st_mtime

    def __ge__(self, othr):
        """self >= othr if self's target modification time >= othr's modification time
        if self's target does not exist return True
        if othr's target does not exist return False
        """
        p_self_target = Path(self.target)
        p_othr_target = Path(othr.target)

        if not p_self_target.exists():
            return True
        elif not p_othr_target.exists():
            return False
        
        return p_self_target.stat().st_mtime >= p_othr_target.stat().st_mtime



