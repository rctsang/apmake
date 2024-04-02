# apmake: Another Python Make System

apmake is another python make system that aims to be gnu make wearing python as a skin and resolves rules bottom-up like `tup`.

the idea is to specify rules in a manner very similar to make, but with the flexibility of the python syntax.

mostly i got sick of trying to remember makefile and bash syntax. make's top-down way of resolving rule dependencies is also a little mindbending to me, and my peanut brain always assumes that if *any* dependency changes in the chain, everything related to it should be recompiled/reprocessed. but writing out every upstream dependency explicitly can be rather annoying.

instead i want to be able to declare new rules in python, and implement build logic in python, while rely on python's subprocess library for any external programs.

for example, instead of this terrifying thing:

```make
define GEN_CD_MAKE_RULE
.PHONY: $(target)
$(target)::
	cd $$(dir $$@) && make
endef

$(foreach target, $(TARGETS), $(eval $(GEN_CD_MAKE_RULE)))
```

do something more like
```py
for target in TARGETS:
	@rule(name=target)
	def action():
		# do things
		Command('echo "doing things"')
```

so yes much of this will be utilizing decorators. hopefully we wind up with something with the same expressive power as make, but with much more flexibility and is more intuitive to use coming from make.

## Installation and Usage

It's not on PyPI (yet) so gotta do it the old fashioned way.

```
pip install -e .
```

Then create Makefile-equivalents (named whatever you want, i haven't thought of a good name and idk if calling everything `apmake.py` is a great idea, as much as i would like to. suggestions welcome.) that look something like the following (see also `examples/simple.py`)

```py
#!/usr/bin/env python3
from apmake import *

@rule(target="example")
def example():
	Command('echo "hello world!"')

# ...
```

Then invoke the script with desired target the same-ish way as Make:

```console
$ ./apmakefile example
hello world!
```

## Notes to Self

~~ok, so first tricky part: figuring out the scheduling algorithm to define the order to invoke the rules. this will be especially important if we want to parallelize, so it would be best if our algorithm took that into account.~~

~~currently i'm thinking of some kind of bfs, where i build up the dependent paths while simultaneously checking for any requisites with a file modify date older than a dependent. when that's found, construct a partial ordering from the dependent paths and build from there.~~ doing the bfs for now.

would like for things to be more like tup, since it's fast and doesn't have the make issue where if some way downstream dependency changes the top level target doesn't do anything if the intermediate file is still present. Probably i'm just using make wrong but i make that mistake often enough that i would like some behavior that does what I want.

tup does things bottom up, but it also relies on persistence of a database that holds the DAG (using sqlite, indexed for fast node lookups) and needs a list of the changed files, which is supposed to be accumulated incrementally. the latter is a tad annoying because while it does make things very fast experientially, there needs to be some infrastructure that tracks that. which i don't like because it adds a bit of complexity with multiple processes running... maybe another day. 

so if i'm generating the list incrementally, i would have to do it on invocation. which should look like a walk down from the target to find outdated requisites, then a walk back up to resolve dependents. I'll just do that for now without saving the list. so the walk happens every time on script invocation.

~~could add in an additional decorator that says don't recurse, just like regular old make. or do that backwards.~~
let's just do things make's way for now and have an `@recurse` decorator that says all of a rule's upstream dependencies should be examined for changes. that will invoke the full BFS every time, instead of make's partial BFS that stops searching subtrees when a dependecy exists.

so that's done and seems to work for the most part. things are very untested, but i'm getting the behavior i want in the `simple.py` example.


## Todo

- [ ] Fix `resolve_reqs` so that `@recurse` will always cause that rule's dependencies to be resolved recursively (checks the entire subtree for outdated dependencies rather than just the top)
- [ ] Verify dependency graph is a DAG (doesn't do that now, probably not good.)
- [x] ~~Double check if the BFS I wrote for finding dependency tree and topological ordering is actually a topological ordering.~~ it should, since it's a partial tree with one root node, so all of it should just correspond to depth
- [ ] Fix the `resolve_reqs` algorithm to take into account the order that dependencies are listed for a rule.

## Helpful Links

- [python decorators](https://realpython.com/primer-on-python-decorators)
- [python singletons](https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/)
- [python operator overloading](https://docs.python.org/3/reference/datamodel.html)
- [topological sort](https://en.wikipedia.org/wiki/Topological_sorting)
- [task scheduling with dependency](https://stackoverflow.com/questions/18314250/)
- [optimal job scheduling](https://en.wikipedia.org/wiki/Optimal_job_scheduling)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [build system rules and algorithms](https://gittup.org/tup/build_system_rules_and_algorithms.pdf) (tup)
- [tup](https://github.com/gittup/tup)
- [BFS for topological sort](https://stackoverflow.com/questions/25229624)

