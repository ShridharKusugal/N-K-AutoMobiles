import json

with open('scripts/resolved_pmb.json', 'r') as f:
    d = json.load(f)

for code, info in d.items():
    name = info['name']
    top = info.get('top')
    if top:
        print(f"[{code}] {name}")
        print(f"    Match: {top['alt']}")
        print(f"    URL:   {top['url']}\n")
    else:
        print(f"[{code}] {name} -> NO MATCH\n")
