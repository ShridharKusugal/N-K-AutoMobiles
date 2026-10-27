import urllib.request
import re

urls = [
    'https://www.deepautomobile.com/bike/hero/splendor-plus',
    'https://partsmybike.com/'
]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
            imgs = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|png|webp)', html)
            print(f"{u} Status: {r.status}, Found {len(imgs)} images")
            for img in imgs[:5]:
                print(f"  {img}")
    except Exception as e:
        print(f"{u} Error: {e}")
