import urllib.request
import re
import urllib.parse

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

queries = [
    'fuel tank',
    'side panel',
    'headlamp cowl',
    'rear mudguard',
    'seat assembly',
    'side stand',
    'centre stand',
    'chain cover',
    'number plate bracket',
    'exhaust heat shield',
    'grab rail',
    'flasher relay',
    'speed sensor',
    'side stand switch',
    'battery cable',
    'front sprocket',
    'rear sprocket',
    'chain master link'
]

results = {}

for q in queries:
    url = f"https://partsmybike.com/?s={urllib.parse.quote(q)}&post_type=product"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            # Look for 300x300 or scaled jpg/png images
            matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
            valid = [(alt, src) for src, alt in matches if 'logo' not in src and 'cropped' not in src]
            results[q] = valid
            print(f"Query '{q}' -> Found {len(valid)} parts")
            for alt, src in valid[:3]:
                print(f"   {alt} -> {src}")
    except Exception as e:
        print(f"Error on {q}: {e}")

print("\n--- SEARCH COMPLETE ---")
