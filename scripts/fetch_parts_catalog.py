import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def search_pmb(query):
    url = f"https://partsmybike.com/?s={urllib.parse.quote_plus(query)}&post_type=product"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
            clean = []
            for src, alt in matches:
                if any(x in src.lower() for x in ['logo', 'banner', 'icon', 'cropped']):
                    continue
                clean.append({'alt': alt.strip(), 'url': src})
            return clean
    except Exception as e:
        return []

SEARCH_MAP = {
    # ENGINE
    'NK-022': ('Cylinder block / barrel', ['cylinder block hero splendor', 'cylinder block kit']),
    'NK-024': ('Connecting rod', ['connecting rod hero splendor', 'connecting rod kit']),
    'NK-025': ('Crankshaft assembly', ['crankshaft complete hero', 'crankshaft assembly pulsar']),
    'NK-026': ('Inlet valve', ['valve inlet hero', 'inlet valve splendor']),
    'NK-027': ('Exhaust valve', ['valve exhaust pulsar', 'exhaust valve hero', 'valve exhaust']),
    'NK-028': ('Valve spring set', ['valve spring set', 'valve spring hero']),
    'NK-029': ('Camshaft', ['camshaft hero honda', 'camshaft assembly splendor']),
    'NK-030': ('Rocker arm set', ['rocker arm set hero', 'rocker arm splendor']),
    'NK-031': ('Timing chain', ['cam chain timing chain hero', 'timing chain splendor']),
    'NK-032': ('Oil pump assembly', ['oil pump assembly hero', 'oil pump pulsar', 'oil pump splendor']),
    'NK-033': ('Oil pump drive gear', ['gear oil pump drive', 'oil pump gear']),
    'NK-034': ('Clutch basket / outer', ['clutch housing outer hero', 'clutch housing splendor', 'clutch outer']),
    'NK-035': ('Clutch hub / inner', ['clutch hub center hero', 'clutch center splendor', 'clutch hub']),
    'NK-036': ('Clutch friction plate set', ['clutch plate genuine hero', 'clutch friction plate set']),
    'NK-037': ('Clutch steel plate set', ['clutch steel plate', 'steel plate clutch']),
    'NK-038': ('Gear shift shaft', ['gear shaft hero splendor', 'gear shift shaft']),
    'NK-039': ('Crankcase gasket', ['crankcase gasket hero', 'clutch cover gasket splendor', 'engine gasket']),
    'NK-040': ('Cylinder head gasket', ['cylinder head gasket hero', 'head gasket splendor']),

    # BRAKES
    'NK-047': ('Front brake lever', ['brake lever front hero', 'front brake lever disc']),
    'NK-048': ('Rear brake pedal', ['brake pedal hero splendor', 'rear brake pedal pulsar', 'brake pedal']),
    'NK-049': ('Front brake master cylinder', ['brake master cylinder pulsar', 'front master cylinder assembly']),
    'NK-050': ('Front brake hose', ['brake hose front disc', 'front brake hose pulsar', 'brake pipe']),
    'NK-051': ('Rear brake cable', ['rear brake cable activa', 'brake cable rear jupiter']),
    'NK-052': ('Brake light switch (front)', ['brake switch front disc', 'front stop switch']),
    'NK-053': ('Brake light switch (rear)', ['rear brake switch hero', 'rear stop switch splendor']),
    'NK-054': ('Brake caliper assembly', ['brake caliper assembly front', 'disc brake caliper pulsar']),
    'NK-055': ('Caliper seal kit', ['caliper seal kit disc', 'brake caliper repair kit', 'caliper ring kit']),
    'NK-056': ('Brake master-cylinder seal kit', ['master cylinder major kit', 'master cylinder kit pulsar']),
    'NK-057': ('Brake fluid DOT specification', ['brake fluid dot 4', 'brake fluid motul dot 3 4']),
    'NK-058': ('Brake drum', ['wheel hub brake drum', 'brake drum rear hero', 'brake drum']),
    'NK-059': ('Brake cam / spindle', ['brake cam rear hero', 'brake arm rear splendor', 'brake cam']),
    'NK-060': ('Brake return spring set', ['brake return spring splendor', 'brake spring hero', 'brake pedal spring']),

    # ELECTRICAL
    'NK-062': ('Spark plug cap', ['spark plug cap hero', 'suppressor cap splendor']),
    'NK-063': ('Regulator-rectifier', ['regulator rectifier hero', 'rr unit splendor', 'regulator rectifier pulsar']),
    'NK-064': ('Starter motor assembly', ['starter motor hero splendor', 'self motor pulsar', 'starter motor']),
    'NK-065': ('Starter relay / solenoid', ['starter relay hero', 'starter relay pulsar', 'starter solenoid']),
    'NK-066': ('Wiring harness', ['wiring harness hero splendor', 'main harness pulsar', 'wire harness']),
    'NK-067': ('Headlamp assembly', ['headlight assembly hero splendor', 'headlamp visor splendor']),
    'NK-068': ('Headlamp bulb', ['headlight bulb 12v 35w', 'halogen headlamp bulb osram', 'headlamp bulb']),
    'NK-069': ('Front indicator lamp (left)', ['indicator lamp hero splendor', 'turn signal light indicator']),
    'NK-072': ('Tail lamp assembly', ['tail light assembly hero splendor', 'tail lamp pulsar']),
    'NK-073': ('Horn switch', ['horn switch hero splendor', 'switch horn button']),
    'NK-074': ('Starter switch', ['self start switch hero', 'starter switch pulsar']),
    'NK-075': ('Ignition switch / lock set', ['lock set hero splendor', 'ignition switch key set splendor']),

    # CHAIN & SPROCKET
    'NK-106': ('Chain slider', ['chain slider hero', 'swingarm chain slider pulsar', 'chain slider']),
    'NK-107': ('Chain guide', ['chain guide rear swingarm', 'drive chain guide', 'chain guide']),
    'NK-108': ('Chain adjuster set', ['chain adjuster hero splendor', 'chain tensioner adjuster set']),
    'NK-109': ('Front sprocket lock plate', ['sprocket lock plate hero', 'front sprocket washer plate', 'sprocket plate']),
    'NK-110': ('Front sprocket nut', ['sprocket nut hero', 'sprocket bolt hero', 'engine sprocket nut']),
    'NK-111': ('Rear sprocket bolt set', ['sprocket bolt set pulsar', 'rear sprocket studs', 'sprocket bolt kit']),
    'NK-112': ('Rear sprocket carrier', ['sprocket carrier pulsar', 'sprocket hub mounting', 'sprocket carrier']),
    'NK-113': ('Cush-drive rubber set', ['coupling rubber hero splendor', 'cush drive rubber set', 'wheel damper']),
    'NK-114': ('Chain roller', ['chain roller guide', 'chain roller tensioner', 'chain roller']),
    'NK-115': ('Chain lubricant', ['chain lube motul', 'chain lubricant spray motul']),
    'NK-116': ('Chain cleaning brush', ['chain cleaning brush motorcycle', 'chain cleaner brush tool']),
    'NK-117': ('Chain guard fastener set', ['chain cover screw set', 'chain guard bolt set']),
    'NK-118': ('Rear axle spacer', ['wheel spacer rear pulsar', 'rear axle spacer hero', 'wheel collar spacer']),
    'NK-119': ('Rear wheel sprocket flange', ['sprocket flange pulsar', 'rear wheel drum flange']),
    'NK-120': ('Chain wear gauge', ['chain wear indicator tool', 'chain gauge ruler'])
}

if __name__ == '__main__':
    resolved = {}
    for code, (name, queries) in SEARCH_MAP.items():
        found = []
        for q in queries:
            res = search_pmb(q)
            if res:
                found.extend(res)
                break
        if found:
            resolved[code] = {'name': name, 'top': found[0], 'all': found[:3]}
            print(f"[{code}] {name} -> {found[0]['alt']} ({found[0]['url']})")
        else:
            resolved[code] = {'name': name, 'top': None}
            print(f"[{code}] {name} -> NO MATCH")

    with open('scripts/resolved_pmb.json', 'w') as f:
        json.dump(resolved, f, indent=2)
    print("\nDone searching! Saved to scripts/resolved_pmb.json")
