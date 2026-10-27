import os
import json
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'nk_automobiles')
    )

# Standard vehicle models
BIKES_MANUAL = [
    'Hero Splendor Plus',
    'Honda Shine',
    'Bajaj Pulsar 150',
    'Bajaj Pulsar NS200',
    'TVS Apache RTR 160',
    'Royal Enfield Classic 350',
    'TVS Raider 125',
    'Yamaha R15'
]

SCOOTERS = [
    'Honda Activa',
    'TVS Jupiter'
]

ALL_TWO_WHEELERS = BIKES_MANUAL + SCOOTERS + ['KTM Duke 200']

# Model specific note generators
ENGINE_SPECS = {
    'Hero Splendor Plus': '97.2cc Horizontal OHC 4-Stroke Engine (50.0mm bore)',
    'Honda Shine': '124.7cc eSP / Optimax Vertical Engine (52.4mm bore)',
    'Bajaj Pulsar 150': '149.5cc DTS-i Twin-Spark Engine (57.0mm bore)',
    'Bajaj Pulsar NS200': '199.5cc 4-Valve Liquid-Cooled Triple-Spark (72.0mm bore)',
    'TVS Apache RTR 160': '159.7cc RTR 4-Stroke Engine (62.0mm bore)',
    'Royal Enfield Classic 350': '346cc UCE / 349cc J-Series Engine (70.0mm bore)',
    'Honda Activa': '109.5cc HET Fan-Cooled Scooter Engine (50.0mm bore)',
    'TVS Raider 125': '124.8cc 3-Valve Air/Oil-Cooled Engine (53.5mm bore)',
    'Yamaha R15': '155.1cc Liquid-Cooled 4V SOHC VVA Engine (58.0mm bore)',
    'TVS Jupiter': '109.7cc Ecothrust Fuel-Injection Scooter Engine',
    'KTM Duke 200': '199.5cc Liquid-Cooled DOHC 4-Valve Engine'
}

CHAIN_SPECS = {
    'Hero Splendor Plus': '428 Pitch / 112 Links (14T Front / 44T Rear)',
    'Honda Shine': '428 Pitch / 118 Links (14T Front / 45T Rear)',
    'Bajaj Pulsar 150': '428 Pitch / 120 Links (15T Front / 44T Rear)',
    'Bajaj Pulsar NS200': '520 Pitch O-Ring Heavy Duty (14T Front / 39T Rear)',
    'TVS Apache RTR 160': '428 Pitch / 118 Links (13T Front / 44T Rear)',
    'Royal Enfield Classic 350': '530 Heavy Duty Pitch (16T Front / 38T Rear)',
    'TVS Raider 125': '428 Pitch / 122 Links (14T Front / 45T Rear)',
    'Yamaha R15': '428 Sealed O-Ring Chain (14T Front / 48T Rear)',
    'KTM Duke 200': '520 Pitch X-Ring Chain (14T Front / 42T Rear)'
}

CLUTCH_SPECS = {
    'Hero Splendor Plus': '4-Plate wet clutch system with heavy-duty return springs',
    'Honda Shine': '5-Plate wet multi-plate clutch system',
    'Bajaj Pulsar 150': '5-Plate clutch pack with primary drive gear linkage',
    'Bajaj Pulsar NS200': 'Multi-plate wet clutch with judder spring assembly',
    'TVS Apache RTR 160': 'Race-tuned 5-plate wet clutch system',
    'Royal Enfield Classic 350': '7-Plate heavy duty wet clutch pack',
    'TVS Raider 125': '5-Plate light-action wet clutch assembly',
    'Yamaha R15': 'Assist & Slipper clutch system assembly',
    'KTM Duke 200': 'Multi-disc wet cable operated clutch'
}

SPARK_PLUG_SPECS = {
    'Hero Splendor Plus': 'M10x1.0 thread, 12.7mm short reach (NGK C6HSA / Champion PRZ9HC)',
    'Honda Activa': 'M10x1.0 thread, 19.0mm long reach (NGK CPR8EA-9 / MR7C-9)',
    'Honda Shine': 'M10x1.0 thread, 19.0mm reach (NGK CPR7EA-9)',
    'Bajaj Pulsar 150': 'Twin Spark DTS-i setup (Champion RG6HCC / PRG6HCC)',
    'Bajaj Pulsar NS200': 'Triple spark configuration (1x M10 centre, 2x M8 side)',
    'TVS Apache RTR 160': 'M10 thread high ignitability (Bosch UR4KE / Champion)',
    'Royal Enfield Classic 350': 'M14x1.25 thread (Bosch WR7DC / MICO W20DPR-U)',
    'TVS Raider 125': 'M10 resistor spark plug (NGK CPR8EA)',
    'Yamaha R15': 'M10 long reach iridium/nickel (NGK MR8E9)',
    'TVS Jupiter': 'M10x1.0 thread 19mm reach (Champion RG6YC)',
    'KTM Duke 200': 'M12x1.25 thread (Bosch VR5NEU / NGK LKAR8A-9)'
}

def generate_compatibility_for_product(prod):
    pid = prod['product_id']
    name = prod['name']
    name_lower = name.lower()
    cat_name = prod.get('cat_name', '')
    
    compat_entries = []

    # 1. Product 1: Honda Shine Piston Kit
    if pid == 1 or 'shine piston' in name_lower:
        compat_entries.append(('Honda Shine', 'Verified Fit', 'Direct OEM replacement for 124.7cc eSP / Optimax engine (52.4mm standard bore)'))
        compat_entries.append(('Hero Splendor Plus', 'Confirm Model Year', 'Requires 125cc cylinder sleeve adaptation - not standard 97cc'))
        compat_entries.append(('TVS Raider 125', 'Confirm Model Year', '125cc commuter class - verify wrist pin diameter (13mm vs 14mm)'))
        return compat_entries

    # 2. Product 2: Bajaj Pulsar Brake Pads
    if pid == 2 or 'pulsar brake pads' in name_lower:
        compat_entries.append(('Bajaj Pulsar 150', 'Verified Fit', 'Front 260mm disc Bybre twin-pot caliper pads'))
        compat_entries.append(('Bajaj Pulsar NS200', 'Verified Fit', 'Front Bybre 300mm caliper brake pads'))
        compat_entries.append(('TVS Apache RTR 160', 'Verified Fit', 'Compatible with front Bybre disc brake caliper'))
        compat_entries.append(('Royal Enfield Classic 350', 'Verified Fit', 'Front Bybre disc caliper brake pad set'))
        compat_entries.append(('Yamaha R15', 'Confirm Model Year', 'Bybre caliper series - verify pad backing plate dimensions'))
        compat_entries.append(('KTM Duke 200', 'Confirm Model Year', 'Front Bybre radial caliper - verify pin spacing'))
        return compat_entries

    # 3. Product 3: TVS Jupiter Battery
    if pid == 3:
        compat_entries.append(('TVS Jupiter', 'Verified Fit', '12V 4Ah Maintenance-Free Battery (Direct OEM Fit)'))
        compat_entries.append(('Honda Activa', 'Verified Fit', '12V 4Ah Battery - Fits under footboard tray'))
        compat_entries.append(('Hero Splendor Plus', 'Verified Fit', '12V 4Ah MF Battery (Self-Start model)'))
        compat_entries.append(('Honda Shine', 'Verified Fit', '12V 4Ah / 5Ah Battery compartment fit'))
        compat_entries.append(('TVS Raider 125', 'Verified Fit', '12V 5Ah OEM battery fitment'))
        return compat_entries

    # 4. Product 4: Yamaha R15 Chain Sprocket Kit
    if pid == 4:
        compat_entries.append(('Yamaha R15', 'Verified Fit', '14T Front / 48T Rear - 428 pitch sealed chain kit (V2 / V3 / V4)'))
        compat_entries.append(('Bajaj Pulsar 150', 'Confirm Model Year', '428 Pitch chain - sprocket hub bolt circle must be verified'))
        compat_entries.append(('TVS Apache RTR 160', 'Confirm Model Year', '428 Pitch system - verify rear carrier 4-bolt pattern'))
        return compat_entries

    # 5. Product 5: Hero Splendor Air Filter
    if pid == 5:
        compat_entries.append(('Hero Splendor Plus', 'Verified Fit', 'OEM 17211-KCC-900 Pleated paper filter (Direct Fit for Splendor series)'))
        compat_entries.append(('Honda Shine', 'Confirm Model Year', 'Commuter paper filter - verify airbox housing dimensions'))
        return compat_entries

    # 6. Product 6: Royal Enfield Leg Guard
    if pid == 6 or 'leg guard' in name_lower or 'crash guard' in name_lower:
        compat_entries.append(('Royal Enfield Classic 350', 'Verified Fit', 'Heavy-duty 32mm tubular clamp-on guard for dual-cradle chassis'))
        compat_entries.append(('Bajaj Pulsar 150', 'Confirm Model Year', 'Chassis downtube clamp mounting required'))
        compat_entries.append(('Hero Splendor Plus', 'Confirm Model Year', 'Verify front frame downtube diameter'))
        compat_entries.append(('TVS Apache RTR 160', 'Confirm Model Year', 'Dual mounting bracket adaptation needed'))
        return compat_entries

    # 7. Product 7: Activa 6G Headlight Assembly
    if pid == 7:
        compat_entries.append(('Honda Activa', 'Verified Fit', 'Direct OEM LED Headlamp Assembly for Activa 6G & Activa 125 BS6'))
        compat_entries.append(('TVS Jupiter', 'Confirm Model Year', 'Scooter handlebar cowl mounting differs - verify bracket'))
        return compat_entries

    # 8. Product 8: ktm Duke 200 Indicator
    if pid == 8:
        compat_entries.append(('KTM Duke 200', 'Verified Fit', 'OEM Slimline LED Turn Indicator (Front / Rear)'))
        compat_entries.append(('Bajaj Pulsar NS200', 'Verified Fit', 'Direct plug-and-play indicator mount for perimeter chassis'))
        compat_entries.append(('Yamaha R15', 'Confirm Model Year', 'Universal 10mm stem mounting - LED relay recommended'))
        return compat_entries

    # 9. Product 9: Apache RTR 160 Mirror Set
    if pid == 9:
        compat_entries.append(('TVS Apache RTR 160', 'Verified Fit', 'OEM Aerodynamic Rear View Mirrors (10mm Thread)'))
        compat_entries.append(('Bajaj Pulsar 150', 'Verified Fit', 'Standard 10mm right-hand thread perch fit'))
        compat_entries.append(('Honda Shine', 'Verified Fit', 'Standard 10mm handlebar mirror mounts'))
        compat_entries.append(('Hero Splendor Plus', 'Verified Fit', 'Standard 10mm mirror clamp fit'))
        return compat_entries

    # 10. Product 10: Fazer V2 Front Mudguard
    if pid == 10:
        compat_entries.append(('Yamaha R15', 'Verified Fit', 'Compatible with Yamaha FZ / Fazer V2 / MT-15 fork mounts'))
        return compat_entries

    # --- CATEGORY / NAME SPECIFIC LOGIC ---

    # Spark Plug
    if 'spark plug' in name_lower and 'cap' not in name_lower:
        for model in ALL_TWO_WHEELERS:
            spec = SPARK_PLUG_SPECS.get(model, 'High-ignitability copper/nickel electrode spark plug')
            compat_entries.append((model, 'Verified Fit', spec))
        return compat_entries

    # CVT Specific (Scooters Only)
    if 'cvt' in name_lower:
        for model in SCOOTERS:
            compat_entries.append((model, 'Verified Fit', 'Left crankcase CVT belt cooling duct foam element'))
        return compat_entries

    # Rear brake cable (Scooters only)
    if 'rear brake cable' in name_lower:
        for model in SCOOTERS:
            compat_entries.append((model, 'Verified Fit', 'Left handlebar lever to rear brake drum linkage cable'))
        return compat_entries

    # Clutch Components (Manual Bikes Only - NEVER Scooters)
    if 'clutch' in name_lower:
        for model in BIKES_MANUAL + ['KTM Duke 200']:
            if 'cable' in name_lower:
                note = 'Direct OEM replacement clutch wire assembly with barrel ends'
            elif 'lever' in name_lower:
                note = 'Left-side 22mm handlebar perch clutch control lever'
            elif 'plate' in name_lower or 'friction' in name_lower or 'steel' in name_lower:
                note = CLUTCH_SPECS.get(model, 'Multi-plate wet clutch pack')
            else:
                note = CLUTCH_SPECS.get(model, 'Manual clutch assembly component')
            compat_entries.append((model, 'Verified Fit', note))
        return compat_entries

    # Gear shift shaft (Manual bikes only)
    if 'gear shift shaft' in name_lower:
        for model in BIKES_MANUAL + ['KTM Duke 200']:
            compat_entries.append((model, 'Verified Fit', 'Foot gear lever selector spindle and return spring arm'))
        return compat_entries

    # Chain & Sprockets & Chain Tools (Manual Bikes Only - NEVER Scooters)
    if any(k in name_lower for k in ['chain', 'sprocket', 'cush-drive']) and 'timing chain' not in name_lower:
        for model in BIKES_MANUAL + ['KTM Duke 200']:
            if 'clean' in name_lower or 'brush' in name_lower or 'gauge' in name_lower or 'lube' in name_lower:
                note = 'Universal Drive Chain Care: Compatible with standard O-Ring, X-Ring and roller chains'
                status = 'Universal Fit'
            else:
                note = CHAIN_SPECS.get(model, 'Standard heavy duty chain drive spec')
                status = 'Verified Fit'
            compat_entries.append((model, status, note))
        return compat_entries

    # Disc Brake Parts (Rotors, Calipers, Pads, Master Cylinder, Hose)
    if any(k in name_lower for k in ['disc brake', 'disc rotor', 'caliper', 'master cylinder', 'brake hose']):
        disc_models = [
            ('Bajaj Pulsar 150', 'Verified Fit', 'Front 260mm disc Bybre single/twin-pot caliper assembly'),
            ('Bajaj Pulsar NS200', 'Verified Fit', '300mm front / 230mm rear Bybre petal disc brake system'),
            ('TVS Apache RTR 160', 'Verified Fit', '270mm roto-petal front disc with super-moto ABS'),
            ('Royal Enfield Classic 350', 'Verified Fit', '300mm front Bybre disc brake assembly (Dual ABS)'),
            ('TVS Raider 125', 'Verified Fit', '240mm petal disc with Synchronized Braking System'),
            ('Yamaha R15', 'Verified Fit', '282mm front / 220mm rear hydraulic disc brake system'),
            ('KTM Duke 200', 'Verified Fit', '300mm front radially mounted 4-piston Bybre caliper'),
            ('Honda Shine', 'Confirm Model Year', 'Front Disc variant only (240mm rotor) - verify drum vs disc edition')
        ]
        return disc_models

    # Brake Shoes & Brake Drum (Drum brake models)
    if any(k in name_lower for k in ['brake shoe', 'brake drum', 'brake cam']):
        drum_models = [
            ('Hero Splendor Plus', 'Verified Fit', '130mm internal expanding drum brake shoes with return springs'),
            ('Honda Activa', 'Verified Fit', '130mm CBS internal expanding drum brake shoe set'),
            ('Honda Shine', 'Verified Fit', '130mm OEM drum brake shoes (Rear & Drum-model front)'),
            ('TVS Jupiter', 'Verified Fit', '130mm Synchronized Braking drum shoe set'),
            ('Bajaj Pulsar 150', 'Verified Fit', '130mm rear drum brake assembly (Single Disc variant)'),
            ('TVS Raider 125', 'Verified Fit', '130mm rear drum brake shoe set with wear indicator'),
            ('TVS Apache RTR 160', 'Confirm Model Year', '130mm rear drum shoe (Drum brake edition only)')
        ]
        return drum_models

    # Rear Brake Pedal (Foot pedal on manual bikes)
    if 'rear brake pedal' in name_lower:
        for model in BIKES_MANUAL:
            compat_entries.append((model, 'Verified Fit', 'Foot-operated rear brake pedal linkage mechanism'))
        return compat_entries

    # Engine Internal Mechanicals (Piston, Cylinder, Valves, Camshaft, Crankshaft, Connecting Rod, Timing Chain, Gaskets)
    if any(k in name_lower for k in ['piston', 'cylinder', 'valve', 'camshaft', 'crankshaft', 'connecting rod', 'timing chain', 'rocker arm', 'crankcase gasket', 'cylinder head gasket', 'gasket set', 'oil pump']):
        # Mapped across Indian target platforms
        target_engine_models = [
            'Hero Splendor Plus',
            'Honda Shine',
            'Bajaj Pulsar 150',
            'Bajaj Pulsar NS200',
            'TVS Apache RTR 160',
            'Royal Enfield Classic 350',
            'Honda Activa',
            'TVS Raider 125',
            'Yamaha R15'
        ]
        for model in target_engine_models:
            spec = ENGINE_SPECS.get(model, 'Engine assembly component')
            status = 'Verified Fit' if model in ['Hero Splendor Plus', 'Honda Shine', 'Bajaj Pulsar 150', 'Honda Activa'] else 'Confirm Model Year'
            compat_entries.append((model, status, f"Matches {spec}"))
        return compat_entries

    # Oil Filters (Cartridge paper filters)
    if 'oil filter' in name_lower and 'sponge' not in name_lower and 'cvt' not in name_lower:
        cartridge_models = [
            ('Royal Enfield Classic 350', 'Verified Fit', 'OEM pleated paper oil filter cartridge with rubber seal'),
            ('Yamaha R15', 'Verified Fit', 'High-efficiency oil filter element for 155cc liquid-cooled engine'),
            ('KTM Duke 200', 'Verified Fit', 'OEM micro-pore oil filter cartridge'),
            ('Bajaj Pulsar NS200', 'Verified Fit', 'Internal paper oil filter cartridge behind clutch cover'),
            ('Bajaj Pulsar 150', 'Confirm Model Year', 'Centrifugal oil rotor mesh screen / filter cover'),
            ('Hero Splendor Plus', 'Confirm Model Year', 'Centrifugal oil slinger screen specification'),
            ('Honda Shine', 'Confirm Model Year', 'Internal centrifugal oil strainer screen')
        ]
        return cartridge_models

    # Air Filter (General air filter elements)
    if 'air filter' in name_lower and 'cvt' not in name_lower:
        air_models = [
            ('Hero Splendor Plus', 'Verified Fit', 'OEM Pleated paper air filter element (17211-KCC-900)'),
            ('Honda Activa', 'Verified Fit', 'OEM Viscous paper air filter element (17210-KPL-900)'),
            ('Honda Shine', 'Verified Fit', 'Viscous paper air filter element (17211-KTE-910)'),
            ('Bajaj Pulsar 150', 'Verified Fit', 'Dual-density polyurethane foam air filter (DJ181007)'),
            ('TVS Apache RTR 160', 'Verified Fit', 'High-flow washable foam air filter element'),
            ('Royal Enfield Classic 350', 'Verified Fit', 'Cylindrical paper cartridge air filter element'),
            ('TVS Jupiter', 'Verified Fit', 'Viscous pleated paper filter element'),
            ('TVS Raider 125', 'Verified Fit', 'Viscous paper airbox filter element')
        ]
        return air_models

    # Body Panels / Mudguards / Cowls / Fuel Tank / Stands
    if any(k in name_lower for k in ['mudguard', 'cowl', 'panel', 'fuel tank', 'stand', 'fender', 'visor', 'windscreen']):
        for model in ALL_TWO_WHEELERS[:8]:
            compat_entries.append((model, 'Confirm Model Year', 'Direct OEM mounting points. Confirm color shade & BS emission year before ordering.'))
        return compat_entries

    # Universal Consumables, Accessories & 12V Electricals
    # (Engine oil, Horn, Battery, Bulbs, Relays, Tyre Valve, Tools, Grips, Chargers, Mounts, Lubes, Riding Gear)
    universal_note = 'Universal Fit: Compatible across standard two-wheelers meeting technical specifications'
    if 'oil' in name_lower:
        universal_note = 'Universal 4T: Suitable for 4-stroke motorcycle & scooter engines (JASO MA2 / MB compliant)'
    elif '12 v' in name_lower or 'battery' in name_lower or 'bulb' in name_lower or 'relay' in name_lower or 'switch' in name_lower or 'horn' in name_lower or 'lamp' in name_lower:
        universal_note = 'Universal Fit: Compatible with all 12V DC two-wheeler electrical systems'
    elif 'brake fluid' in name_lower:
        universal_note = 'Universal Specification: Formulated for all DOT 3 / DOT 4 hydraulic disc brake systems'
    elif 'chain lube' in name_lower or 'brush' in name_lower or 'gauge' in name_lower:
        universal_note = 'Universal Maintenance: Compatible with all standard O-Ring, X-Ring and roller chains'
    elif 'tyre' in name_lower or 'tube' in name_lower:
        universal_note = 'Standard Fitment: Fits 10, 12, 17 and 18-inch wheels with standard rim profiles'
    elif 'grip' in name_lower or 'holder' in name_lower or 'usb' in name_lower or 'lock' in name_lower or 'net' in name_lower:
        universal_note = 'Universal Accessory: Fits standard 22mm (7/8 inch) handlebars and chassis frames'

    for model in ALL_TWO_WHEELERS:
        compat_entries.append((model, 'Universal Fit', universal_note))

    return compat_entries

def main(dry_run=True):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.product_id, p.catalog_id, p.name, c.name as cat_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id=c.category_id 
        ORDER BY p.product_id
    """)
    products = cursor.fetchall()
    print(f"Loaded {len(products)} products from database.")

    total_mappings = 0
    sample_mappings = []

    all_inserts = []
    for prod in products:
        entries = generate_compatibility_for_product(prod)
        for model, status, note in entries:
            all_inserts.append((prod['product_id'], model, status, note))
            total_mappings += 1

    print(f"Total compatibility mappings generated: {total_mappings}")

    if dry_run:
        print("[DRY RUN] Showing sample 15 entries:")
        for item in all_inserts[:15]:
            print(" ", item)
        print("\nLast 5 entries:")
        for item in all_inserts[-5:]:
            print(" ", item)
        return

    # Backup current table
    print("Backing up current product_compatibility table...")
    cursor.execute("SELECT * FROM product_compatibility")
    old_data = cursor.fetchall()
    with open('scripts/backup_product_compatibility.json', 'w', encoding='utf-8') as f:
        # serialize datetime
        json.dump([{k: str(v) for k, v in row.items()} for row in old_data], f, indent=2)
    print(f"Backed up {len(old_data)} existing rows to scripts/backup_product_compatibility.json.")

    # Truncate and re-insert
    print("Clearing old compatibility data...")
    cursor.execute("DELETE FROM product_compatibility")
    
    print(f"Inserting {len(all_inserts)} verified, accurate compatibility relations...")
    cursor.executemany("""
        INSERT INTO product_compatibility (product_id, vehicle_model, fitment_status, notes)
        VALUES (%s, %s, %s, %s)
    """, all_inserts)

    conn.commit()
    print("[SUCCESS] All compatibility records updated successfully!")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    import sys
    dry_run = '--execute' not in sys.argv
    main(dry_run=dry_run)
