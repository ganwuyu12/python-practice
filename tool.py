from pathlib import Path
import sys

def count_files(directory):
    p = Path(directory)
    if not p.exists():
        print("Directory does not exist.")
        return None
    if not p.is_dir():
        print("Path is not a directory.")
        return None
    result = {}
    for file in p.iterdir():
        if file.is_file():
            suffix = file.suffix
            result[suffix] = result.get(suffix, 0) + 1
    return result

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    result = count_files(directory)
    if result is not None:
        for suffix, count in result.items():
            print(f"{suffix}: {count}")