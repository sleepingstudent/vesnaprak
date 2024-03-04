import shlex


a = input()
b = input()

print('register', shlex.join([a, b]))
