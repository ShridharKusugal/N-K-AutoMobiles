import urllib.request
import re
import urllib.parse

models = [
    'hero/splendor-plus',
    'honda/activa',
    'honda/shine',
    'bajaj/pulsar-150',
    'tvs/apache-rtr-160',
    'royal-enfield/classic-350'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for m in models:
    url = f'https://www.deepautomobile.com/bike/{m}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            # Extract cards with image and title
            matches = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', html)
            # Filter out logos
            parts = [(alt, src) for alt, src in matches if 'deep-logo' not in src and 'brand-logo' not in src]
            print(f"Model: {m} -> Found {len(parts)} parts")
            for alt, src in parts[:8]:
                # extract s3 URL if inside _next/image
                if 'url=' in src:
                    parsed_s3 = urllib.parse.unquote(src.split('url=')[1].split('&')[0])
                else:
                    parsed_s3 = src
                print(f"   {alt} -> {parsed_s3}")
    except Exception as e:
        print(f"Error on {m}: {e}")
