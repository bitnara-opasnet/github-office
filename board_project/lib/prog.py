import argparse

parser = argparse.ArgumentParser()
# parser.add_argument("--echo", help="echo the string you use here")
# parser.add_argument("--verbose", action="store_true", help="increase output verbosity")
# parser.add_argument("square", help="display a square of a given number",type=int)
parser.add_argument("x", type=int, help="the base")
parser.add_argument("y", type=int, help="the exponent")
parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="count", default=0)
args = parser.parse_args()
ans = args.x**args.y

if args.verbosity >= 2:
    print("Running '{}'".format(__file__))
if args.verbosity >=1:
    print("{}^{} == ".format(args.x, args.y), end="")
print(ans)