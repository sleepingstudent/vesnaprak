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