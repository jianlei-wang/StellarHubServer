import os
from typing import List, Dict


def list_directory(path: str) -> List[Dict]:
    """ 读取目录 """
    if not os.path.exists(path):
        raise Exception("路径不存在")

    items = []
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        is_dir = os.path.isdir(full_path)
        size = os.path.getsize(full_path) if not is_dir else 0
        items.append({
            "name": name,
            "isDir": is_dir,
            "path": full_path,
            "size": size
        })
    return items


def read_text_file(path: str) -> str:
    """ 读取文本文件，自动兼容 UTF-8 / GBK """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        with open(path, "r", encoding="gbk") as f:
            return f.read()
