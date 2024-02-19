import zlib
with open("../../.git/objects/41/9dd696613ebe8061c00660c8db3c8ebadbf432", "rb") as ff:
    contents = ff.read()

print(ff)
print(contents)
print(zlib.decompress(contents))
