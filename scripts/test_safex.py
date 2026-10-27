import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search_safex(query):
    # Safexbikes has a search URL: https://www.safexbikes.com/search/{query} or https://www.safexbikes.com/
    url = f"https://www.safexbikes.com/search/{urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            # Look for cloudinary images: https://res.cloudinary.com/safexbikes-com/image/upload/...
            matches = re.findall(r'(https://res\.cloudinary\.com/safexbikes-com/image/upload/[^"\'\s>]+)', html)
            imgs = list(dict.fromkeys(matches)) # deduplicate
            return imgs
    except Exception as e:
        return [f"Err: {e}"]

if __name__ == '__main__':
    for q in ["clutch housing splendor", "clutch hub splendor", "crankcase gasket splendor", "head gasket splendor"]:
        imgs = search_safex(q)
        print(f"Safex '{q}': {len(imgs)} imgs")
        for img in imgs[:3]:
            print(f"  {img}")
