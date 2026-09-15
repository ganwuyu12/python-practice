from pathlib import Path
import sys

def count_py_files(directory):
    p=Path(directory)
    if not p.is_dir():
        print("Path is not a directory.")
        return None
    count=0
    for file in p.iterdir():
        if file.is_file() and file.suffix==".py":
            count+=1
    return count

if __name__ == '__main__':
    directory=sys.argv[1] if len(sys.argv)>1 else "."
    result=count_py_files(directory)
    print(f"Number of .py files in {directory}: {result}")