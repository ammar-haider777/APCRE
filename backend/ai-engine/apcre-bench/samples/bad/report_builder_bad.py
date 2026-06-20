import time

ALL_REPORTS = []

def make_report(title, rows, fmt, dest, send_email, email_addr, cc_list):
    global ALL_REPORTS
    out = ""
    out = out + "REPORT: " + title + "\n"
    out = out + "DATE: " + str(time.time()) + "\n"
    out = out + "=" * 40 + "\n"
    for r in rows:
        line = ""
        for c in r:
            line = line + str(c) + " | "
        out = out + line + "\n"
    out = out + "=" * 40 + "\n"
    if fmt == "txt":
        f = open(dest, "w")
        f.write(out)
        f.close()
    elif fmt == "csv":
        f = open(dest, "w")
        for r in rows:
            f.write(",".join([str(c) for c in r]) + "\n")
        f.close()
    if send_email:
        print("Sending to " + email_addr)
        for cc in cc_list:
            print("CC: " + cc)
    ALL_REPORTS.append(out)
    return out
