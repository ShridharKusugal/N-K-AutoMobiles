import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request('https://www.deepautomobile.com/sitemap.xml', headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    xml = r.read().decode('utf-8', errors='ignore')
    urls = re.findall(r'<loc>(https?://[^\s<]+)</loc>', xml)

# Find product URLs
part_urls = [u for u in urls if '/part/' in u or '/product/' in u]
print(f"Total part/product URLs: {len(part_urls)}")
for u in part_urls[:20]:
    print("  ", u)
