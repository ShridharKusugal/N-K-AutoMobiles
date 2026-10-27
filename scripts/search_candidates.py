import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search_pmb(query):
    url = f"https://partsmybike.com/?s={urllib.parse.quote_plus(query)}&post_type=product"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
            res = []
            for src, alt in matches:
                if 'logo' in src.lower() or 'banner' in src.lower() or 'icon' in src.lower():
                    continue
                res.append({'alt': alt.strip(), 'url': src})
            return res
    except Exception as e:
        return [{'error': str(e)}]

def search_deep(query):
    url = f"https://www.deepautomobile.com/category/engine" # can also inspect
    # or general search
    return []

if __name__ == '__main__':
    items = [
        "cylinder block hero splendor",
        "connecting rod hero splendor",
        "crankshaft hero splendor",
        "inlet valve hero splendor",
        "exhaust valve hero honda",
        "valve spring hero honda",
        "camshaft hero honda",
        "rocker arm hero honda",
        "timing chain hero honda",
        "oil pump hero honda",
        "oil pump drive gear",
        "clutch basket hero honda",
        "clutch hub center hero honda",
        "clutch plate hero honda",
        "clutch steel plate",
        "gear shift shaft hero honda",
        "crankcase gasket hero honda",
        "cylinder head gasket hero honda"
    ]
    for q in items:
        res = search_pmb(q)
        print(f"\n=== Query: {q} ===")
        for r in res[:2]:
            print(f"  {r.get('alt')} -> {r.get('url')}")
