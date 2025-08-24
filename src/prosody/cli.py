"""CLI entry point for prosody demos."""

import argparse
from pathlib import Path
from typing import Optional

from .demo_mlk import run_demo


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(prog="prosody", description="Prosody demonstration commands")
    subparsers = parser.add_subparsers(dest="command")

    demo = subparsers.add_parser("demo-mlk", help="Render the 'I Have a Dream' excerpt")
    demo.add_argument("--out", required=True, help="Path to output WAV file")
    demo.add_argument("--voice", help="Override voice name")
    demo.add_argument("--dry-run", action="store_true", help="Print render plan without audio")
    demo.add_argument("--seed", type=int, help="Random seed for reproducible variations")

    args = parser.parse_args(argv)

    if args.command == "demo-mlk":
        out_path = Path(args.out)
        run_demo(out_path, args.voice, args.dry_run, args.seed)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
