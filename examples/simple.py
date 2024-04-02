from apmake import *


@rule(target="hello")
def action():
    Command("echo \"hello world!\"")

@rule(target="compound")
def action():
    Command("echo \"this is a compound command\"") \
    and Command("echo \"print this if the previous command suceeded\"")

@rule(target="environment")
def environment():
    Command(f"echo {ENV['CONDA_PREFIX']}")
    # Command("echo $CONDA_PREFIX")

@rule(target="deps", requires=['hello', 'compound'])
def action():
    print("I ran the prerequisites")
    ENV['TMP'] = "deps_done!"

@rule(target="kwargs", param="testing")
def action(param):
    print(f"param: {param}")

@rule(target="deep", requires=["deps"])
def action():
    print(f"{ENV['TMP']}")
    ENV['TMP'] = "deep_done!"

@recurse
@rule(target="verydeep", requires=["deep"])
def action():
    print(f"{ENV['TMP']}")