import argparse
import shutil
from pathlib import Path


def cleanup_all_generated() -> None:
    generated_dir = Path("generated")
    if not generated_dir.exists():
        print("Generated directory doesn't exist.")
        return
    file_count = 0
    for item in generated_dir.rglob("*"):
        if item.is_file():
            file_count += 1
            item.unlink()
    for item in generated_dir.rglob("*"):
        if item.is_dir() and not any(item.iterdir()):
            item.rmdir()
    print(f"✅ Cleaned up generated directory: {file_count} files removed")


def cleanup_temp_files() -> None:
    generated_dir = Path("generated")
    if not generated_dir.exists():
        print("Generated directory doesn't exist.")
        return
    removed_count = 0
    for item in generated_dir.rglob("*"):
        if item.is_file() and ('temp' in item.name.lower() or 'test' in item.name.lower()):
            item.unlink()
            removed_count += 1
    print(f"✅ Temp/test cleanup completed: {removed_count} files removed")


def show_disk_usage() -> None:
    dirs_to_check = ["generated", "."]
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if not path.exists():
            continue
        total_size = 0
        file_count = 0
        for item in path.rglob("*"):
            if item.is_file() and item.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                total_size += item.stat().st_size
                file_count += 1
        if file_count > 0:
            size_mb = total_size / (1024 * 1024)
            print(f"📁 {dir_path}: {file_count} audio files, {size_mb:.1f} MB")


def one_line_cleanup() -> None:
    print("⚠️  One-line cleanup: Searching for temp/test files...")
    current_dir = Path('.')
    total_cleaned = 0
    for item in current_dir.rglob("*"):
        try:
            if 'temp' in item.name.lower() or 'test' in item.name.lower():
                if item.is_file():
                    item.unlink()
                    total_cleaned += 1
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    total_cleaned += 1
        except Exception:
            continue
    print(f"✅ One-line cleanup completed: {total_cleaned} items removed")


def run(args: argparse.Namespace) -> None:
    if args.all:
        cleanup_all_generated()
    elif args.temp:
        cleanup_temp_files()
    elif args.disk_usage:
        show_disk_usage()
    elif args.one_line:
        one_line_cleanup()
    else:
        print("No cleanup option selected")


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        'cleanup',
        help='Remove generated audio and temporary files',
        description='Utility commands to tidy up generated audio for your podcast.',
        epilog='Example: main cleanup --all',
    )
    parser.add_argument('--all', action='store_true', help='Remove all files from generated/')
    parser.add_argument('--temp', action='store_true', help="Remove files with 'temp' or 'test' in name")
    parser.add_argument('--disk-usage', action='store_true', help='Show disk usage of audio directories')
    parser.add_argument('--one-line', action='store_true', help="Delete all 'temp' or 'test' files everywhere")
    parser.set_defaults(func=run)
