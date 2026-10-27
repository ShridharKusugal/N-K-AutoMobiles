import urllib.request
import re
import urllib.parse
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

urls_to_scan = [
    'https://www.deepautomobile.com/bike/hero/splendor-plus',
    'https://www.deepautomobile.com/bike/honda/shine',
    'https://www.deepautomobile.com/bike/bajaj/pulsar-150',
    'https://www.deepautomobile.com/bike/tvs/apache-rtr-160',
    'https://www.deepautomobile.com/bike/tvs/jupiter',
    'https://www.deepautomobile.com/bike/hero/passion-pro',
    'https://www.deepautomobile.com/category/handlebar-and-controls',
    'https://www.deepautomobile.com/category/brake-system',
    'https://www.deepautomobile.com/category/electrical',
    'https://www.deepautomobile.com/category/tyres-and-wheels',
    'https://www.deepautomobile.com/category/engine'
]

results = []

for u in urls_to_scan:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', html)
            for alt, src in matches:
                if 'deep-logo' in src or 'brand-logo' in src or 'Neon' in src or not alt.strip():
                    continue
                if 'url=' in src:
                    s3_url = urllib.parse.unquote(src.split('url=')[1].split('&')[0])
                else:
                    s3_url = src
                results.append((alt.strip(), s3_url))
    except Exception as e:
        print(f"Error on {u}: {e}")

print(f"Total parts collected: {len(results)}")

# Search for keywords
keywords = ['cable', 'seal', 'gasket', 'horn', 'tube', 'spoke', 'lamp', 'oil', 'plug', 'shoe', 'pad', 'rubber']
for kw in keywords:
    matched = [r for r in results if kw.lower() in r[0].lower()]
    print(f"\nKeyword '{kw}': {len(matched)} matches:")
    for m in matched[:4]:
        print(f"  {m[0]} -> {m[1]}")
