import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search_partsmybike(query):
    url = f"https://partsmybike.com/?s={query.replace(' ', '+')}&post_type=product"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
            print(f"PartsMyBike query '{query}' -> Found {len(matches)} results")
            for src, alt in matches[:5]:
                print(f"  {alt} -> {src}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    search_partsmybike('clutch cable')
    search_partsmybike('throttle cable')
    search_partsmybike('engine oil')
    search_partsmybike('fuel hose')
    search_partsmybike('horn')
