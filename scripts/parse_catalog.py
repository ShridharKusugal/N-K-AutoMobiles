import urllib.request
import re
import json

url = 'https://www.deepautomobile.com/bike/hero/splendor-plus'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            data = json.loads(m.group(1))
            props = data.get('props', {}).get('pageProps', {})
            # Look for product lists anywhere in pageProps
            print('pageProps keys:', list(props.keys()))
            items = props.get('parts', props.get('products', props.get('items', [])))
            print('Found items count:', len(items))
            for item in items[:15]:
                print(item.get('name'), '->', item.get('image') or item.get('imageUrl') or item.get('thumbnail'))
        else:
            # regex search for product cards
            cards = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', html)
            print('Found img cards:', len(cards))
            for alt, src in cards[:15]:
                print(f"{alt} -> {src}")
except Exception as e:
    print('Error:', e)
