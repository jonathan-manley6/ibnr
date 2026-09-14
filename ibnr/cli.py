"""python -m ibnr reserve --data DIR --out FILE"""
import argparse
import json

from .data import Extract
from .reserve import reserve


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ibnr")
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("reserve", help="the reserve for claims incurred on or before the valuation date")
    r.add_argument("--data", required=True)
    r.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    result = reserve(Extract(args.data))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    return 0
