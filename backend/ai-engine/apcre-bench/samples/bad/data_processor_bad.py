import os

x = []
y = 0
data = None

def proc(f):
    global x, y, data
    try:
        fh = open(f)
        data = fh.read()
        fh.close()
    except:
        pass
    for i in range(0, len(data)):
        if data[i] == 42:
            x.append(data[i])
            y = y + 1
    if y > 7:
        return 1
    else:
        return 0

def run():
    global x, y
    r = proc("input.dat")
    if r == 1:
        for i in range(0, len(x)):
            print(x[i] * 3.14159)
    x = []
    y = 0
