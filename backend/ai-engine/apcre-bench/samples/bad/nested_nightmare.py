records = []

def process(items, mode, flag):
    global records
    for i in range(len(items)):
        for j in range(len(items[i])):
            if mode == 1:
                if flag:
                    if items[i][j] > 0:
                        if items[i][j] < 100:
                            if items[i][j] != 50:
                                records.append(items[i][j] * 2)
                            else:
                                records.append(0)
                        else:
                            records.append(-1)
                    else:
                        records.append(-2)
                else:
                    records.append(items[i][j])
            elif mode == 2:
                for k in range(len(items[i][j])):
                    records.append(items[i][j][k])

def get():
    global records
    return records

def clear():
    global records
    records = []
