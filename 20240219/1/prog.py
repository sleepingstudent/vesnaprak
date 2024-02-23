import os
import zlib
from glob import iglob
import sys

arg = sys.argv[1:]
repo_path = arg[0]
refs_heads_dir = os.path.join(repo_path, '.git', 'refs', 'heads')

if len(arg) == 1:
    print(*os.listdir(refs_heads_dir), sep='\n')
else:
    br_name = arg[1]
    branch_file_path = os.path.join(refs_heads_dir, br_name)

    if not os.path.exists(branch_file_path):
        sys.exit()

    with open(branch_file_path, "r") as fd:
        commit_sha = fd.read().strip()

    objects_dir = os.path.join(repo_path, '.git', 'objects')
    objects_path = os.path.join(objects_dir, commit_sha[:2], commit_sha[2:])

    with open(objects_path, "rb") as fd:
        obj = zlib.decompress(fd.read())

    header, _, body = obj.partition(b'\x00')

    print(body.decode())
    tree_sha = body.decode().split('\n', 1)[0].split()[1]

    with open(os.path.join(objects_dir, tree_sha[:2], tree_sha[2:]), "rb") as fd:
        tree_obj, _, tail = zlib.decompress(fd.read()).partition(b'\x00')

    while tail:
        treeobj, _, tail = tail.partition(b'\x00')
        tmode, tname = treeobj.split()
        num, tail = tail[:20], tail[20:]
        if tmode[:3] == b'100':
            print(f"blob {num.hex()}\t{tname.decode()}")
        else:
            print(f"tree {num.hex()}\t{tname.decode()}")
    print()
    while body.decode().split('\n', 2)[1].split()[0] == "parent":
        print(f"TREE for commit {commit_sha}")

        tree_sha = body.decode().split('\n', 1)[0].split()[1]

        with open(os.path.join(objects_dir, tree_sha[:2], tree_sha[2:]), "rb") as fd:
            tree_obj, _, tail = zlib.decompress(fd.read()).partition(b'\x00')

        while tail:
            treeobj, _, tail = tail.partition(b'\x00')
            tmode, tname = treeobj.split()
            num, tail = tail[:20], tail[20:]
            if tmode[:3] == b'100':
                print(f"blob {num.hex()}\t{tname.decode()}")
            else:
                print(f"tree {num.hex()}\t{tname.decode()}")

        commit_sha = body.decode().split('\n', 2)[1].split()[1]
        objects_path = os.path.join(objects_dir, commit_sha[:2], commit_sha[2:])

        flag = True
        i = 2

        while not os.path.exists(objects_path):
            flag = False
            if body.decode().split('\n', i+1)[i].split()[0] != "parent":
                break
            while not flag:
                if body.decode().split('\n', i+1)[i].split()[0] == "parent":
                    commit_sha = body.decode().split('\n', i+1)[i].split()[1]
                    objects_path = os.path.join(objects_dir, commit_sha[:2], commit_sha[2:])
                    flag = True
                else:
                    break

                i += 1

        if flag:
            with open(objects_path, "rb") as fd:
                obj = zlib.decompress(fd.read())

            header, _, body = obj.partition(b'\x00')
        else:
            break