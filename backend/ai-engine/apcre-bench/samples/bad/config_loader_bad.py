import json

def load():
    f = open("C:/Users/admin/config.json")
    d = json.loads(f.read())
    f.close()
    return d

def save(d):
    f = open("C:/Users/admin/config.json", "w")
    f.write(json.dumps(d))
    f.close()

def get_val(d, k):
    return d[k]

def set_val(d, k, v):
    d[k] = v
    save(d)
