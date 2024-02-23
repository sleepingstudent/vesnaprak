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
    pass
