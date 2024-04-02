# apmake: Another Python Make System

apmake is another python make system that aims to be gnu make wearing python as a skin and resolves rules bottom-up like `tup`.

the idea is to specify rules in a manner very similar to make, but with the flexibility of the python syntax.

mostly i got sick of trying to remember makefile and bash syntax. make's top-down way of resolving rule dependencies is also a little mindbending to me, and my peanut brain always assumes that if *any* dependency changes in the chain, everything related to it should be recompiled/reprocessed. but writing it all out explicitly can be rather annoying.

want to be able to declare new rules in python, implement build logic in python, and just rely on subprocess for any external programs.

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
```

so yes much of this will be utilizing decorators. hopefully we wind up with something with the same expressive power as make, but with much more flexibility and is more intuitive to use coming from make.


## Notes

ok, so first tricky part: figuring out the scheduling algorithm to define the order to invoke the rules. this will be especially important if we want to parallelize, so it would be best if our algorithm took that into account.

currently i'm thinking of some kind of bfs, where i build up the dependent paths while simultaneously checking for any requisites with a file modify date older than a dependent. when that's found, construct a partial ordering from the dependent paths and build from there.


tup does things bottom up, but it also relies on persistence of a database that holds the DAG (using sqlite, indexed for fast node lookups) and needs a list of the changed files, which is supposed to be accumulated incrementally. the latter is a tad annoying because while it does make things very fast experientially, there needs to be some infrastructure that tracks that. which i don't like because it adds a bit of complexity with multiple processes running... maybe another day. 

so if i'm generating the list incrementally, i would have to do it on invocation. which should look like a walk down from the target to find outdated requisites, then a walk back up to resolve dependents.

could add in an additional decorator that says don't recurse, just like regular old make. or do that backwards.

let's just do things make's way for now.


so that's done and seems to work for the most part.


## Todo

[ ] Fix `resolve_reqs` so that `@recurse` will always cause that rule's dependencies to be resolved recursively (checks the entire subtree for outdated dependencies rather than just the top)


