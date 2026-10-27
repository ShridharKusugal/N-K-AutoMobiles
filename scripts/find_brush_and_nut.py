import urllib.request
import urllib.parse
import re

headers = {'User-Agent': 'Mozilla/5.0'}
for q in ['chain cleaner brush', 'chain brush', 'sprocket nut hero', 'sprocket bolt hero']:
    url = f"https://partsmybike.com/?s={urllib.parse.quote_plus(q)}&post_type=product"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
            print(f"=== {q} ===")
            for src, alt in matches[:3]:
                if 'logo' not in src:
                    print(f"  {alt} -> {src}")
    except Exception as e:
        print(f"Error {q}: {e}")
