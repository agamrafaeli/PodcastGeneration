import argparse
import asyncio

import generate
import sample
import cleanup


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Podcast generation toolkit',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    for mod in (generate, sample, cleanup):
        mod.register(subparsers)
    args = parser.parse_args(argv)
    result = args.func(args)
    if asyncio.iscoroutine(result):
        asyncio.run(result)


if __name__ == '__main__':
    main()
