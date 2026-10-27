import urllib.request
import urllib.parse
import json
import re

def search_ddg_image(query):
    url = "https://duckduckgo.com/"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        req = urllib.request.Request("https://duckduckgo.com/?" + urllib.parse.urlencode(params), headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode("utf-8", errors="ignore")
            m = re.search(r'vqd=([\d-]+)&', html) or re.search(r'vqd="([^"]+)"', html)
            if not m:
                return None
            vqd = m.group(1)
            
        i_url = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={urllib.parse.quote(query)}&vqd={vqd}&f=,,,&p=1"
        req2 = urllib.request.Request(i_url, headers=headers)
        with urllib.request.urlopen(req2, timeout=5) as r2:
            data = json.loads(r2.read().decode("utf-8"))
            results = data.get("results", [])
            for res in results:
                img_url = res.get("image")
                if img_url and (img_url.endswith(".jpg") or img_url.endswith(".png") or img_url.endswith(".jpeg")):
                    return img_url
    except Exception as e:
        print(f"Error searching {query}: {e}")
    return None

if __name__ == "__main__":
    for q in ["motorcycle air filter element", "motorcycle foam air filter", "motorcycle oil filter spin on"]:
        res = search_ddg_image(q)
        print(f"{q} -> {res}")
