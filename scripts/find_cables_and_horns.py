import urllib.request
import re
import urllib.parse

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

urls_to_scan = [
    'https://www.deepautomobile.com/bike/honda/activa-6g',
    'https://www.deepautomobile.com/bike/honda/shine',
    'https://www.deepautomobile.com/bike/hero/splendor-plus',
    'https://www.deepautomobile.com/bike/hero/glamour',
    'https://www.deepautomobile.com/bike/bajaj/pulsar-150',
    'https://www.deepautomobile.com/bike/bajaj/platina-110',
    'https://www.deepautomobile.com/bike/tvs/apache-rtr-160',
    'https://www.deepautomobile.com/bike/royal-enfield/bullet-350',
    'https://www.deepautomobile.com/bike/royal-enfield/classic-350',
    'https://www.deepautomobile.com/category/accessories',
    'https://www.deepautomobile.com/category/handlebar-and-controls',
    'https://www.deepautomobile.com/category/lighting',
    'https://www.deepautomobile.com/category/fuel-system',
    'https://www.deepautomobile.com/category/brake-system'
]

results = []

for u in urls_to_scan:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
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

search_terms = ['clutch', 'accel', 'throttle', 'gasket', 'horn', 'hose', 'plug', 'oil', 'fuel', 'pack']
for term in search_terms:
    m = [r for r in results if term.lower() in r[0].lower()]
    print(f"\n--- Matches for '{term}' ({len(m)} found): ---")
    for item in m[:5]:
        print(f"  {item[0]} -> {item[1]}")
