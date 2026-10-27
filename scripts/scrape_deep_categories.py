import urllib.request
import re
import urllib.parse

categories = [
    'engine',
    'brake-system',
    'chain-and-sprocket',
    'electrical',
    'lighting',
    'body-parts',
    'tyres-and-wheels',
    'suspension',
    'fuel-system',
    'exhaust-system',
    'handlebar-and-controls'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

found_parts = {}

for cat in categories:
    url = f"https://www.deepautomobile.com/category/{cat}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', html)
            cat_parts = []
            for alt, src in matches:
                if 'deep-logo' in src or 'brand-logo' in src or 'Neon' in src or not alt.strip():
                    continue
                # Extract image url
                if 'url=' in src:
                    s3_url = urllib.parse.unquote(src.split('url=')[1].split('&')[0])
                else:
                    s3_url = src
                cat_parts.append((alt.strip(), s3_url))
            found_parts[cat] = cat_parts
            print(f"Category '{cat}' -> Found {len(cat_parts)} parts")
            for alt, s3 in cat_parts[:4]:
                print(f"   {alt} -> {s3}")
    except Exception as e:
        print(f"Error on {cat}: {e}")

print(f"\nTotal categories scraped: {len(found_parts)}")
