store = {}

def add(key, value, cache={}):
    cache[key] = value
    store[key] = value
    return cache

def get(key, default=0):
    try:
        return store[key]
    except:
        return default

def remove(key):
    try:
        del store[key]
    except:
        pass

def clear(store={}):
    store = {}
    return store

def size():
    global store
    return len(store)
