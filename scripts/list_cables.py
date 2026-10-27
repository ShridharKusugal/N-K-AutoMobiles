import urllib.request
import re
import urllib.parse

headers = {'User-Agent': 'Mozilla/5.0'}
urls = ['https://www.deepautomobile.com/category/handlebar-and-controls', 'https://www.deepautomobile.com/bike/hero/splendor-plus', 'https://www.deepautomobile.com/bike/honda/activa-6g']
for u in urls:
    req = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        matches = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', r.read().decode('utf-8', errors='ignore'))
        for alt, src in matches:
            if 'cable' in alt.lower() or 'clutch' in alt.lower() or 'brake' in alt.lower():
                s3 = urllib.parse.unquote(src.split('url=')[1].split('&')[0]) if 'url=' in src else src
                print(f"{alt} -> {s3}")
