# -*- coding: utf-8 -*-
"""VULNERABLE: OS command injection via shell=True - for benchmark only."""

import subprocess
import os


def list_files(directory):
    result = subprocess.run("ls -la " + directory, shell=True, capture_output=True)
    return result.stdout.decode()


def ping_host(hostname):
    output = subprocess.check_output(
        "ping -c 4 " + hostname, shell=True
    )
    return output.decode()


def cleanup_temp(user_path):
    os.system("rm -rf " + user_path)


def compress_logs(log_dir, archive_name):
    cmd = f"tar -czf {archive_name} {log_dir}"
    subprocess.Popen(cmd, shell=True)
