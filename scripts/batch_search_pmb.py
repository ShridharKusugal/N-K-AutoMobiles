import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def search_pmb(queries):
    for q in queries:
        url = f"https://partsmybike.com/?s={urllib.parse.quote_plus(q)}&post_type=product"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode('utf-8', errors='ignore')
                matches = re.findall(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"', html)
                clean = []
                for src, alt in matches:
                    if any(x in src.lower() for x in ['logo', 'banner', 'icon', 'cropped']):
                        continue
                    clean.append((alt.strip(), src))
                if clean:
                    return clean
        except Exception as e:
            pass
    return []

# Remaining products grouped
ENGINE_ITEMS = [
    ('NK-022', 43, 'Cylinder block / barrel', ['cylinder block hero splendor', 'cylinder block kit']),
    ('NK-024', 45, 'Connecting rod', ['connecting rod hero splendor', 'connecting rod kit']),
    ('NK-025', 46, 'Crankshaft assembly', ['crankshaft complete hero', 'crankshaft assembly pulsar']),
    ('NK-026', 47, 'Inlet valve', ['valve inlet hero', 'inlet valve splendor']),
    ('NK-027', 48, 'Exhaust valve', ['valve exhaust hero', 'exhaust valve splendor', 'valve exhaust']),
    ('NK-028', 49, 'Valve spring set', ['valve spring hero', 'valve spring set', 'valve spring']),
    ('NK-029', 50, 'Camshaft', ['camshaft hero honda', 'camshaft assembly splendor']),
    ('NK-030', 51, 'Rocker arm set', ['rocker arm set hero', 'rocker arm splendor']),
    ('NK-031', 52, 'Timing chain', ['cam chain timing chain hero', 'timing chain splendor']),
    ('NK-032', 53, 'Oil pump assembly', ['oil pump assembly hero', 'oil pump splendor', 'oil pump pulsar']),
    ('NK-033', 54, 'Oil pump drive gear', ['gear oil pump drive', 'oil pump gear']),
    ('NK-034', 55, 'Clutch basket / outer', ['clutch housing hero', 'clutch outer splendor', 'clutch housing']),
    ('NK-035', 56, 'Clutch hub / inner', ['clutch hub center hero', 'clutch center splendor', 'clutch hub']),
    ('NK-036', 57, 'Clutch friction plate set', ['clutch plate genuine hero', 'clutch friction plate set']),
    ('NK-037', 58, 'Clutch steel plate set', ['clutch steel plate', 'steel plate clutch']),
    ('NK-038', 59, 'Gear shift shaft', ['gear shaft hero splendor', 'gear shift shaft']),
    ('NK-039', 60, 'Crankcase gasket', ['crankcase gasket hero', 'clutch cover gasket splendor', 'magneto cover gasket']),
    ('NK-040', 61, 'Cylinder head gasket', ['cylinder head gasket hero', 'head gasket splendor', 'head gasket kit'])
]

BRAKE_ITEMS = [
    ('NK-047', 68, 'Front brake lever', ['brake lever front hero', 'front brake lever disc']),
    ('NK-048', 69, 'Rear brake pedal', ['brake pedal hero splendor', 'rear brake pedal pulsar', 'brake pedal']),
    ('NK-049', 70, 'Front brake master cylinder', ['brake master cylinder pulsar', 'front master cylinder assembly']),
    ('NK-050', 71, 'Front brake hose', ['brake hose front disc', 'front brake hose pulsar', 'brake pipe']),
    ('NK-051', 72, 'Rear brake cable', ['rear brake cable activa', 'brake cable rear jupiter']),
    ('NK-052', 73, 'Brake light switch (front)', ['brake switch front disc', 'front stop switch']),
    ('NK-053', 74, 'Brake light switch (rear)', ['rear brake switch hero', 'rear stop switch splendor']),
    ('NK-054', 75, 'Brake caliper assembly', ['brake caliper assembly front', 'disc brake caliper pulsar']),
    ('NK-056', 77, 'Brake master-cylinder seal kit', ['master cylinder major kit', 'caliper seal kit']),
    ('NK-057', 78, 'Brake fluid DOT specification', ['brake fluid dot 4', 'brake oil motul']),
    ('NK-058', 79, 'Brake drum', ['brake drum rear hero', 'wheel hub brake drum']),
    ('NK-059', 80, 'Brake cam / spindle', ['brake cam rear hero', 'brake arm rear splendor', 'brake cam']),
    ('NK-060', 81, 'Brake return spring set', ['brake spring hero', 'brake return spring splendor', 'brake pedal spring'])
]

ELECTRICAL_ITEMS = [
    ('NK-062', 83, 'Spark plug cap', ['spark plug cap hero', 'suppressor cap splendor', 'spark plug cap']),
    ('NK-063', 84, 'Regulator-rectifier', ['regulator rectifier hero', 'rr unit splendor', 'regulator rectifier pulsar']),
    ('NK-064', 85, 'Starter motor assembly', ['starter motor hero splendor', 'self motor pulsar', 'starter motor']),
    ('NK-065', 86, 'Starter relay / solenoid', ['starter relay hero', 'starter relay pulsar', 'starter solenoid']),
    ('NK-066', 87, 'Wiring harness', ['wiring harness hero splendor', 'main harness pulsar', 'wire harness']),
    ('NK-067', 88, 'Headlamp assembly', ['headlight assembly hero splendor', 'headlamp visor splendor']),
    ('NK-068', 89, 'Headlamp bulb', ['headlight bulb 12v 35w', 'halogen headlamp bulb osram']),
    ('NK-069', 90, 'Front indicator lamp (left)', ['indicator lamp hero splendor', 'turn signal light indicator']),
    ('NK-072', 93, 'Tail lamp assembly', ['tail light assembly hero splendor', 'tail lamp pulsar']),
    ('NK-073', 94, 'Horn switch', ['horn switch hero splendor', 'switch horn button']),
    ('NK-074', 95, 'Starter switch', ['self start switch hero', 'starter switch pulsar']),
    ('NK-075', 96, 'Ignition switch / lock set', ['lock set hero splendor', 'ignition switch key set splendor'])
]

CHAIN_ITEMS = [
    ('NK-106', 127, 'Chain slider', ['chain slider hero', 'swingarm chain slider pulsar', 'chain slider']),
    ('NK-107', 128, 'Chain guide', ['chain guide rear swingarm', 'drive chain guide']),
    ('NK-108', 129, 'Chain adjuster set', ['chain adjuster hero splendor', 'chain tensioner adjuster set']),
    ('NK-109', 130, 'Front sprocket lock plate', ['sprocket lock plate hero', 'front sprocket washer plate']),
    ('NK-110', 131, 'Front sprocket nut', ['sprocket nut hero', 'sprocket bolt hero']),
    ('NK-111', 132, 'Rear sprocket bolt set', ['sprocket bolt set pulsar', 'rear sprocket studs']),
    ('NK-112', 133, 'Rear sprocket carrier', ['sprocket carrier pulsar', 'sprocket hub mounting']),
    ('NK-113', 134, 'Cush-drive rubber set', ['coupling rubber hero splendor', 'cush drive rubber set']),
    ('NK-114', 135, 'Chain roller', ['chain roller guide', 'chain roller bearing']),
    ('NK-115', 136, 'Chain lubricant', ['chain lube motul', 'chain lubricant spray']),
    ('NK-116', 137, 'Chain cleaning brush', ['chain cleaning brush motorcycle', 'chain cleaner brush']),
    ('NK-117', 138, 'Chain guard fastener set', ['chain cover screw set', 'chain guard bolt']),
    ('NK-118', 139, 'Rear axle spacer', ['wheel spacer rear pulsar', 'rear axle spacer hero']),
    ('NK-119', 140, 'Rear wheel sprocket flange', ['sprocket flange pulsar', 'rear wheel drum flange']),
    ('NK-120', 141, 'Chain wear gauge', ['chain wear indicator tool', 'chain gauge ruler'])
]

def run_group(name, items):
    print(f"\n=================== {name} ({len(items)} items) ===================")
    results = {}
    for cat_id, pid, pname, queries in items:
        found = search_pmb(queries)
        if found:
            alt, url = found[0]
            print(f"[{cat_id}] {pname} -> MATCH: {alt[:40]}... URL: {url}")
            results[cat_id] = {'pid': pid, 'name': pname, 'url': url, 'alt': alt}
        else:
            print(f"[{cat_id}] {pname} -> NOT FOUND")
            results[cat_id] = {'pid': pid, 'name': pname, 'url': None}
    return results

if __name__ == '__main__':
    all_res = {}
    all_res['engine'] = run_group('ENGINE', ENGINE_ITEMS)
    all_res['brakes'] = run_group('BRAKES', BRAKE_ITEMS)
    all_res['electrical'] = run_group('ELECTRICAL', ELECTRICAL_ITEMS)
    all_res['chain'] = run_group('CHAIN & SPROCKET', CHAIN_ITEMS)
    with open('scripts/search_results.json', 'w') as f:
        json.dump(all_res, f, indent=2)
    print("\nSaved all search results to scripts/search_results.json")
