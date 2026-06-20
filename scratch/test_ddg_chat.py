try:
    from duckduckgo_search import DDGS
    print("duckduckgo_search imported successfully!")
    with DDGS() as ddgs:
        reply = ddgs.chat("Hello! Who are you?", model='claude-3-haiku')
        print(f"Reply: {reply}")
except Exception as e:
    print(f"Error: {e}")
