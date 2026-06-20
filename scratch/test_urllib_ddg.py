import urllib.request
import urllib.parse
import json

def get_vqd():
    url = "https://duckduckgo.com/duckchat/v1/status"
    req = urllib.request.Request(url)
    req.add_header("x-vqd-accept", "1")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    try:
        with urllib.request.urlopen(req) as res:
            return res.info().get("x-vqd-4")
    except Exception as e:
        print(f"Error fetching VQD: {e}")
        return None

def chat_ddg(message):
    vqd = get_vqd()
    print(f"VQD: {vqd}")
    if not vqd:
        return "Error: No VQD token"
        
    url = "https://duckduckgo.com/duckchat/v1/chat"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}]
    }
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("x-vqd-4", vqd)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "text/event-stream")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    try:
        with urllib.request.urlopen(req) as res:
            reply = []
            while True:
                line = res.readline()
                if not line:
                    break
                decoded = line.decode('utf-8').strip()
                if decoded.startswith("data: "):
                    data_str = decoded[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data_json = json.loads(data_str)
                        if "message" in data_json:
                            reply.append(data_json["message"])
                    except Exception as e:
                        pass
            return "".join(reply)
    except Exception as e:
        return f"Exception in chat: {e}"

if __name__ == "__main__":
    resp = chat_ddg("Hello! Who are you?")
    print(f"Response:\n{resp}")
