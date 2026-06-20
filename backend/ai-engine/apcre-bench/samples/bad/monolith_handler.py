import json, os, sys

def handle_everything(action, payload, db_path, log_path, retries):
    result = None
    if action == "read":
        f = open(db_path)
        raw = f.read()
        f.close()
        result = json.loads(raw)
        lf = open(log_path, "a")
        lf.write("read done\n")
        lf.close()
    elif action == "write":
        f = open(db_path, "w")
        f.write(json.dumps(payload))
        f.close()
        lf = open(log_path, "a")
        lf.write("write done\n")
        lf.close()
    elif action == "delete":
        os.remove(db_path)
        lf = open(log_path, "a")
        lf.write("delete done\n")
        lf.close()
    elif action == "retry":
        for i in range(0, retries):
            try:
                handle_everything("read", payload, db_path, log_path, 0)
            except:
                pass
    elif action == "validate":
        if payload is None:
            return -1
        if len(str(payload)) < 3:
            return -2
        if len(str(payload)) > 10000:
            return -3
        return 0
    return result
