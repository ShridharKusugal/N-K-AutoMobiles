import urllib.request
import urllib.parse
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search(q):
    url = f"https://partsmybike.com/?s={urllib.parse.quote_plus(q)}&post_type=product"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
            clean = []
            for src, alt in matches:
                if any(x in src.lower() for x in ['logo', 'banner', 'icon']):
                    continue
                clean.append((alt.strip(), src))
            return clean
    except Exception as e:
        return [(str(e), '')]

queries = {
    'NK-028 (Valve spring set)': ['valve spring splendor', 'valve spring zadon', 'valve spring set'],
    'NK-058 (Brake drum)': ['brake drum rear activa', 'rear brake drum dio', 'brake drum'],
    'NK-062 (Spark plug cap)': ['suppressor cap hero', 'spark plug cap ngk', 'plug cap'],
    'NK-110 (Front sprocket nut)': ['sprocket nut pulsar', 'front sprocket nut', 'countershaft nut'],
    'NK-111 (Rear sprocket bolt set)': ['sprocket bolt pulsar', 'rear sprocket bolt kit', 'sprocket stud'],
    'NK-116 (Chain cleaning brush)': ['chain cleaning brush', 'chain brush', 'grunge brush'],
    'NK-117 (Chain guard fastener set)': ['chain cover screw', 'chain cover bolt', 'chain guard bolt'],
    'NK-119 (Rear wheel sprocket flange)': ['sprocket flange', 'coupling flange rear', 'sprocket hub pulsar'],
    'NK-120 (Chain wear gauge)': ['chain wear indicator', 'chain wear gauge', 'chain checker tool']
}

for item, qlist in queries.items():
    print(f"\n================ {item} ================")
    found = False
    for q in qlist:
        results = search(q)
        if results and results[0][1]:
            print(f"Query '{q}' -> {results[0][0]} ({results[0][1]})")
            found = True
            break
    if not found:
        print("NO MATCH")
