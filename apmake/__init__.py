import os
import sys
import argparse
from copy import copy
from atexit import register
from typing import Callable, Optional
from collections import namedtuple, defaultdict

from apmake.command import Command
from apmake.rule import Rule

class Environment:
    """a singleton class for accessing environment variables (wrapper for os.environ)"""
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Environment, cls).__new__(cls)
        return cls._instance

    def __getitem__(self, key):
        """get a variable: `ENV['VAR']`
        note: returns an empty string if variable doesn't exist
        """
        return os.getenv(key, "")

    def __setitem__(self, key, value):
        """set a variable: `ENV['VAR'] = 'VALUE'`
        note: variables set in a python script will not be set in the shell
        and will only influence actions taken in the script or its subprocesses
        """
        os.environ[key] = value

    def __delitem__(self, key):
        """delete a variable: `del ENV['VAR']`
        note: variables unset in a python script will not be unset in the shell
        """
        del os.environ[key]

ENV = Environment()


class Runner:
    """a singleton class for tracking and running rules and handling dependency"""
    _rules = defaultdict(Rule)

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Runner, cls).__new__(cls)
        return cls._instance


    def add(self, rule : Rule, overrule : bool = False):
        """register a rule with the runner
        if the target already exists, execute added rule in addition 
        to the target's previously registered rules in order of addition
        unless 'overrule' parameter is specified.
        return the updated rule
        """
        if (rule.target not in self._rules) or overrule:
            self._rules[rule.target] = rule
            for req in rule.deps:
                self._rules[req].ders.add(rule.target)
        else:
            self._rules[rule.target] |= rule

        return self._rules[rule.target]


    def run(self, target : Optional[str] = None, parallel : bool = False):
        """run all the rules that need to be updated"""
        if not target:
            # use the first found target as the default rule
            target = next(iter(self._rules))

        work_queue = self.resolve_reqs(target)

        for target in work_queue:
            self._rules[target]()

    def resolve_reqs(self, target : str):
        """return a list of rules that need to be run based on target
        by default, looks for outdated rules in a top-down manner, like make
        """
        invoked_rule = self._rules[target]

        if invoked_rule.recurse:
            return self._resolve_reqs_recursive(target)

        dep_rules = [self._rules[dep] for dep in invoked_rule.deps]

        outdated = {invoked_rule.target}
        depths = {}
        queue = [(target, 0)]
        while queue:
            target, depth = queue.pop(0)
            
            if target in depths:
                if depth > depths[target]:
                    depths[target] = depth
                continue

            depths[target] = depth

            rule = self._rules[target]

            if rule > invoked_rule:
                outdated.add(rule.target)

                for dep in rule.deps:
                    queue.append((dep, depth + 1))

        ordering = list(sorted(outdated, key=lambda k: depths[k], reverse=True))

        return ordering



    def _resolve_reqs_recursive(self, target : str):
        """returns a list of rules that need to be run based on target
        returns an empty list if all targets are up to date
        returns a list of all rules whose dependencies or targets 
        are outdated in order sorted by dependency
        (earlier rules must be completed before later rules)
        """
        invoked_rule = self._rules[target]

        # # update bidirectional dependencies
        # for target, rule in self._rules.items():
        #     for prereq in rule.deps:
        #         self._rules[prereq].ders.add(target)

        # calculate topological ordering and find out of date dependencies
        # visit in bfs order to calculate depth
        depths = {}
        outdated = {target}
        path = []
        queue = [(target, path)]
        while queue:
            (target, path) = queue.pop(0)
            depth = len(path)

            # check visited
            if target in depths:
                # update visited if necessary
                if depth > depths[target]:
                    depths[target] = depth
                    outdated |= set(path)
                continue

            # add to visited and paths
            depths[target] = depth
            path.append(target)

            rule = self._rules[target]

            if rule > invoked_rule:
                outdated |= set(path)

            # add children
            for prereq in rule.deps:
                queue.append((prereq, copy(path)))

        ordering = list(sorted(outdated, 
            key=lambda k: depths[k],
            reverse=True))

        return ordering



_runner = Runner()

def rule(target : str, 
        requires : list[str] = [], 
        overrule : bool = False, 
        **kwargs
    ):
    """the rule decorator to specify a function as a rule for a target 
    dependencies (prerequisite targets) can also be specified, 
    as well as any kwargs to invoke the rule's function with
    returns the created rule, which is callable
    """
    def make_rule(func : Callable):
        rule = Rule(
            target=target, 
            func=func, 
            reqs=requires,
            **kwargs
        )

        return _runner.add(rule, overrule=overrule)

    return make_rule


def recurse(rule : Callable):
    """decorator to specify that a rule's dependencies should be recursively
    checked for outdatedness
    """
    assert isinstance(rule, Rule), "@recurse must decorate a rule (outside @rule)"
    rule.recurse = True
    return rule


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=str, nargs='?', default=None,
        help="invoke rule for specified target")

    args = parser.parse_args()

    _runner.run(args.target)


register(_cli)
