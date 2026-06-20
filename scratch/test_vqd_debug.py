import urllib.request
import urllib.parse
import json
import traceback

def get_vqd():
    url = "https://duckduckgo.com/duckchat/v1/status"
    req = urllib.request.Request(url)
    req.add_header("x-vqd-accept", "1")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    try:
        with urllib.request.urlopen(req) as res:
            print(f"Status Code: {res.status}")
            print(f"Headers: {res.info()}")
            return res.info().get("x-vqd-4")
    except Exception as e:
        print(f"Error fetching VQD:")
        traceback.print_exc()
        return None

get_vqd()
