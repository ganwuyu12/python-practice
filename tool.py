from pathlib import Path
import sys

def count_files(directory):
    # TODO 1: 用 Path() 把 directory 变成路径对象，存到变量 p
    p = Path(directory)
    # TODO 2: 判断 p 是否存在且是目录，不是就打印提示并 return None
    if not p.exists():
        print("Directory does not exist.")
        return None
    if not p.is_dir():
        print("Path is not a directory.")
        return None
    # TODO 3: 造一个空 dict 存结果
    result = {}
    # TODO 4: 遍历 p 下所有文件，按后缀计数
    for file in p.iterdir():
        if file.is_file():
            suffix = file.suffix
            result[suffix] = result.get(suffix, 0) + 1
    # TODO 5: 返回这个 dict
    return result

if __name__ == '__main__':
    # TODO 6: 从 sys.argv 拿第一个参数
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    # TODO 7: 调用 count_files，打印结果
    result = count_files(directory)
    if result is not None:
        for suffix, count in result.items():
            print(f"{suffix}: {count}")