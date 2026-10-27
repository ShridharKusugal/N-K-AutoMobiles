import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search_deep_auto(query):
    url = f"https://www.deepautomobile.com/search?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if m:
                data = json.loads(m.group(1))
                props = data.get('props', {}).get('pageProps', {})
                print(f"Query '{query}' - Props keys: {list(props.keys())}")
                # Search across all lists in props
                for k, v in props.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        print(f"  List '{k}' has {len(v)} items. First item: {v[0].get('name', v[0].get('title'))}")
            else:
                matches = re.findall(r'<img[^>]+alt="([^"]+)"[^>]+src="([^"]+)"', html)
                print(f"Query '{query}' - Found {len(matches)} HTML img tags")
                for name, src in matches[:5]:
                    print(f"  {name} -> {src}")
    except Exception as e:
        print(f"Error searching '{query}': {e}")

if __name__ == '__main__':
    search_deep_auto('cable')
    search_deep_auto('gasket')
    search_deep_auto('oil seal')
