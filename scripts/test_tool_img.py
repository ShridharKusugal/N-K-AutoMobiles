import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
urls = [
    'https://www.motionpro.com/images/products/08-0674_main.jpg',
    'https://m.media-amazon.com/images/I/71ZpT7iYFCL._SL1500_.jpg', # Chain wear checker
    'https://m.media-amazon.com/images/I/61k1qV1q0IL._SL1500_.jpg'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"Success: {u} (code {r.status}, size {len(r.read())})")
    except Exception as e:
        print(f"Failed {u}: {e}")
