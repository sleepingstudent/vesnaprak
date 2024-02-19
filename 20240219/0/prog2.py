#!/usr/bin/env python3

import zlib
from glob import iglob
from os.path import basename, dirname
SHFT = "  "
for history in iglob("../../.git/objects/??/*"):
    id = basename(dirname(history)) + basename(history)

    with open(history, "rb") as f:
        obj = zlib.decompress(f.read())
        header, _, bdy = obj.partition(b'\x00')
        kind, size = header.split()
    print("ID:", id, kind.decode())
    if kind == b'tree':
        endpart = bdy
        while endpart:
            treeobj, _, endpart = endpart.partition(b'\x00')
            tmode, tname = treeobj.split()
            num, endpart = endpart[:20], endpart[20:]
            print(f"{SHFT}{tname.decode()} {tmode.decode()} {num.hex()}")
    elif kind == b'commit':
        out = bdy.decode().replace('\n', '\n' + SHFT)
        print(f"{SHFT}{out}")
    elif kind == b'blob':
        print(bdy.decode())
