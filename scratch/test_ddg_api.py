import requests
import json

def get_vqd():
    url = "https://duckduckgo.com/duckchat/v1/status"
    headers = {"x-vqd-accept": "1", "User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    return res.headers.get("x-vqd-4")

def chat_ddg(message):
    try:
        vqd = get_vqd()
        print(f"VQD: {vqd}")
        if not vqd:
            return "Error: No VQD token"
            
        url = "https://duckduckgo.com/duckchat/v1/chat"
        headers = {
            "x-vqd-4": vqd,
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": message}]
        }
        res = requests.post(url, headers=headers, json=payload, stream=True)
        print(f"Status Code: {res.status_code}")
        
        reply = []
        for line in res.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    data_str = decoded[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data_json = json.loads(data_str)
                        # The text content is usually in the "message" key
                        if "message" in data_json:
                            reply.append(data_json["message"])
                    except Exception as e:
                        pass
        return "".join(reply)
    except Exception as e:
        return f"Exception: {e}"

if __name__ == "__main__":
    resp = chat_ddg("Hello! Who are you?")
    print(f"Response:\n{resp}")
