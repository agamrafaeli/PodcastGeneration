"""Command-line interface for prosody utilities."""
from __future__ import annotations

import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prosody")
    sub = parser.add_subparsers(dest="command")

    demo = sub.add_parser("demo-mlk", help="Run the MLK 'I Have a Dream' demo")
    demo.add_argument("--out", required=True, help="Output WAV file path")
    demo.add_argument("--voice", help="Voice override")
    demo.add_argument("--dry-run", action="store_true", help="Print render plan without audio")
    demo.add_argument("--seed", type=int, help="Random seed for reproducible variations")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo-mlk":
        from prosody.demo_mlk import run_demo_mlk
        return run_demo_mlk(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
