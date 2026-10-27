import json

with open('scripts/resolved_pmb.json', 'r') as f:
    d = json.load(f)

for code in ['NK-022', 'NK-024', 'NK-025', 'NK-026', 'NK-027', 'NK-028', 'NK-029', 'NK-030', 'NK-031', 'NK-032', 'NK-033', 'NK-034', 'NK-035', 'NK-036', 'NK-037', 'NK-038', 'NK-039', 'NK-040']:
    item = d.get(code)
    if item and item.get('top'):
        print(f"[{code}] {item['name']} -> {item['top']['alt']} ({item['top']['url']})")
    else:
        print(f"[{code}] -> NO MATCH")
