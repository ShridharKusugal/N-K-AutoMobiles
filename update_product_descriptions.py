import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Detailed product descriptions
product_descriptions = {
    1: """Original Honda Piston Kit for Shine 125cc motorcycles. This genuine OEM replacement piston kit ensures optimal engine performance and longevity. Manufactured with high-grade aluminum alloy, it features precision-machined surfaces for perfect cylinder fit. The kit includes piston, piston rings, gudgeon pin, and circlips. Designed to withstand high temperatures and pressures, providing excellent compression and fuel efficiency. Compatible with Honda Shine, Shine SP, and CB Shine models. Recommended replacement at 40,000-50,000 km for maintaining peak engine performance.""",
    
    2: """Premium quality front disc brake pads specifically designed for Bajaj Pulsar 150 series. These high-performance brake pads feature semi-metallic compound that provides excellent stopping power in all weather conditions. Heat-resistant formula prevents brake fade during aggressive riding. Low dust formulation keeps your wheels cleaner. Includes wear indicator for timely replacement. Compatible with Pulsar 150, 150 NS, and 150 AS models. Noise-free braking with minimal vibration. Easy installation with included shims and anti-rattle clips. Recommended replacement every 15,000-20,000 km or when pad thickness reaches 2mm.""",
    
    3: """High-capacity 4LB (12V 4Ah) maintenance-free battery designed for TVS Jupiter scooters. This sealed lead-acid battery features advanced AGM (Absorbent Glass Mat) technology for superior performance and reliability. Spill-proof design with leak-proof construction ensures safe operation in all riding positions. Pre-charged and ready to install - no acid filling required. Excellent cold cranking performance for easy starts in all weather. Vibration-resistant construction for longer life. Compatible with TVS Jupiter, Jupiter Grande, and Jupiter Classic models. Typical lifespan of 2-3 years with proper maintenance. Includes 6-month manufacturer warranty.""",
    
    4: """Professional-grade brass chain sprocket kit for Yamaha R15 V3 motorcycles. This complete drive train kit includes front sprocket (15T), rear sprocket (52T), and premium O-ring chain (428H-120L). Manufactured from high-strength brass alloy for exceptional wear resistance and durability. Precision-cut teeth ensure smooth power transfer and reduced noise. Heat-treated for maximum strength and longevity. The O-ring chain features sealed lubrication for extended life and minimal maintenance. Perfect for both street riding and track use. Improves acceleration and top speed characteristics. Complete installation hardware included. Recommended replacement every 25,000-30,000 km.""",
    
    5: """High-efficiency foam air filter designed for Hero Splendor Plus motorcycles. This washable and reusable air filter provides superior filtration while maintaining excellent airflow for optimal engine performance. Made from premium-grade polyurethane foam with precise pore size for maximum dust retention. Pre-oiled and ready to install. Filters particles down to 5 microns, protecting your engine from harmful contaminants. Improves throttle response and fuel efficiency. Easy to clean - simply wash with mild detergent, dry, re-oil, and reinstall. Environmentally friendly alternative to disposable paper filters. Compatible with Hero Splendor Plus, Splendor iSmart, and Passion Pro models. Can last up to 50,000 km with proper cleaning and maintenance.""",
    
    6: """Heavy-duty stainless steel leg guard (crash guard) for Royal Enfield Classic 350 motorcycles. This premium protection accessory is constructed from 25mm diameter 304-grade stainless steel tubing with mirror-polished finish. Provides excellent protection to engine, body panels, and rider's legs in case of falls or accidents. Engineered to absorb impact without damaging the motorcycle frame. Precision-bent to follow the bike's contours for perfect fit and aesthetic appeal. Powder-coated mounting brackets for corrosion resistance. Easy bolt-on installation with all necessary hardware included. Does not interfere with center stand or side stand operation. Adds a rugged, adventure-ready look to your Classic 350. Backed by 1-year warranty against manufacturing defects.""",
    
    7: """Genuine Honda Activa 6G complete headlight assembly with integrated position lamp. This OEM replacement unit features advanced multi-reflector technology for superior illumination and wider beam spread. Crystal-clear polycarbonate lens with UV protection prevents yellowing and maintains clarity over time. Includes H4 halogen bulb socket (bulb sold separately) and LED position lamp. Plug-and-play installation with original connectors - no wiring modifications required. Weather-sealed housing protects against water ingress and dust. Aerodynamic design complements the Activa 6G's styling. Meets all automotive lighting standards for road safety. Perfect replacement for damaged or faded headlight units. Includes mounting brackets and adjustment screws for precise beam alignment.""",
    
    8: """Premium LED turn signal indicators for KTM Duke 200/250/390 motorcycles. These high-visibility indicators feature ultra-bright amber LEDs with sequential flowing animation for enhanced visibility and modern styling. Compact, aerodynamic design reduces wind resistance. Smoked lens with clear LED illumination for aggressive appearance. Built-in resistors prevent hyper-flashing - no additional load resistors required. IP67 waterproof rating ensures reliable operation in all weather conditions. CNC-machined aluminum housing with anodized finish. Universal M10 threaded stem fits most motorcycles. Easy plug-and-play installation. Set includes front and rear indicators (4 pieces total). Consumes 90% less power than conventional bulb indicators. Virtually maintenance-free with 50,000+ hour LED lifespan.""",
    
    9: """Aerodynamic rear-view mirror set for TVS Apache RTR 160 motorcycles. These sport-style mirrors feature convex glass for wider field of view, reducing blind spots and enhancing safety. Sleek, low-profile design minimizes wind resistance at high speeds. Sturdy ABS plastic housing with chrome accents for premium appearance. Adjustable ball-joint mechanism allows 360-degree positioning for perfect viewing angle. Anti-vibration mounting reduces mirror shake at high RPMs. Easy bolt-on replacement for stock mirrors. Set includes left and right mirrors with all mounting hardware. Fits Apache RTR 160, 160 4V, and 180 models. Shatter-resistant glass construction. Improves both functionality and aesthetics of your motorcycle.""",
    
    10: """Stylish red front mudguard (fender) for Yamaha Fazer V2 motorcycles. This genuine Yamaha accessory is manufactured from high-impact ABS plastic with UV-resistant red paint finish that won't fade in sunlight. Precision-molded to match OEM specifications for perfect fit and finish. Protects the engine and rider from mud, water, and road debris. Aerodynamic design reduces drag and complements the Fazer's sporty styling. Pre-drilled mounting holes for easy installation. Includes stainless steel mounting hardware and detailed installation instructions. Lightweight yet durable construction. Also available in black and blue colors (sold separately). Enhances the visual appeal while providing practical protection. Direct replacement for worn or damaged original mudguard.""",
    
    11: """Professional-grade motorcycle riding gloves by Pakilo. These full-finger gloves are designed for all-season riding comfort and protection. Constructed with premium synthetic leather palm for excellent grip and durability. Breathable mesh fabric on back of hand provides ventilation and flexibility. Reinforced knuckle protection with TPU armor absorbs impact. Touch-screen compatible fingertips allow smartphone use without removing gloves. Adjustable wrist strap with hook-and-loop closure ensures secure fit. Foam padding on palm reduces vibration fatigue on long rides. Reflective piping enhances visibility in low-light conditions. Available in multiple sizes (M, L, XL, XXL). Machine washable for easy maintenance. Ideal for daily commuting, touring, and recreational riding.""",
    
    12: """High-performance clutch plate set designed for 150cc and above motorcycles. This premium aftermarket kit includes friction plates, steel plates, and clutch springs for complete clutch renewal. Manufactured from advanced friction material with high heat resistance and excellent grip characteristics. Provides smoother engagement and better power transfer compared to stock clutch. Reduces clutch slip during aggressive acceleration and high-load situations. Compatible with popular 150-200cc bikes including Pulsar, Apache, FZ, and similar models. Easy installation with standard tools. Significantly improves clutch life and performance. Ideal for riders who demand better clutch feel and durability. Includes detailed fitment guide. Recommended for both street and performance applications.""",
    
    13: """Professional LED fog light kit with complete wiring harness and handlebar switch. This dual-lamp setup provides powerful auxiliary lighting for improved visibility in fog, rain, and night riding conditions. Each lamp features 10W CREE LED producing 1000 lumens of bright white light (6000K color temperature). Adjustable mounting brackets allow precise beam angle adjustment. IP67 waterproof rating ensures reliable operation in harsh weather. Includes relay, fuse, and plug-and-play wiring harness for safe installation. Universal fitment for most motorcycles. Handlebar-mounted on/off switch with LED indicator. Aluminum housing with efficient heat dissipation. Low power consumption (20W total) won't drain your battery. Significantly improves visibility and safety during adverse conditions.""",
    
    14: """Full system stainless steel exhaust designed for performance motorcycles. This Akrapovic-style exhaust system delivers significant power gains, weight reduction, and aggressive exhaust note. Constructed from high-grade 304 stainless steel with TIG-welded seams for maximum durability. Includes header pipe, mid-pipe, and slip-on muffler with removable DB killer. Improves exhaust flow, resulting in 3-5 HP increase and better throttle response. Reduces weight by approximately 40% compared to stock exhaust. Deep, throaty sound that's loud enough to be noticed but not obnoxiously loud. Heat-resistant black coating on muffler. Includes all mounting hardware and gaskets. Fits 150-250cc sport bikes. Professional installation recommended. May require ECU remapping for optimal performance.""",
    
    15: """Universal digital instrument cluster by Koso featuring speedometer, tachometer, and multiple functions. This modern gauge replaces outdated analog instruments with crisp LCD display and LED backlighting. Shows speed (MPH/KPH switchable), RPM, odometer, dual trip meters, fuel level, engine temperature, voltage, and clock. Programmable shift light with adjustable RPM warning. Maximum speed and RPM recall function. Compact 2.5-inch display fits most motorcycles. Includes speed sensor, temperature sensor, and complete wiring harness. Water-resistant construction (IP65 rated). Easy-to-read display in all lighting conditions. Customizable display colors. Universal fitment with detailed installation manual. Perfect upgrade for custom builds or replacing damaged stock gauges.""",
    
    16: """Premium waterproof seat cover by Autoform designed for maximum comfort and protection. This anti-slip seat cover features 3D mesh construction that promotes air circulation, keeping you cool during hot weather. Waterproof outer layer protects your seat from rain and spills. Elastic edges ensure secure fit without slipping. Reduces heat absorption - seat stays cooler in direct sunlight. Easy to install and remove for cleaning. Universal size fits most motorcycle and scooter seats (length: 60-80cm). Durable polyester construction resists tearing and fading. Adds extra cushioning for improved riding comfort on long journeys. Protects original seat upholstery from wear, sun damage, and stains. Available in black color. Machine washable. Ideal for daily commuters and touring riders.""",
    
    17: """Large diameter 300mm disc brake rotor for enhanced braking performance. This Brembo-style floating rotor features two-piece construction with stainless steel braking surface and aluminum carrier. Provides significantly better stopping power and heat dissipation compared to smaller rotors. Wave-cut design reduces weight while maintaining strength. Improves brake modulation and reduces brake fade during aggressive riding. Compatible with most sport bikes and performance motorcycles (verify fitment before purchase). Includes mounting hardware. Precision-machined braking surface ensures smooth, vibration-free operation. Corrosion-resistant finish. Recommended for riders seeking maximum braking performance. Professional installation and brake system bleeding required. May require caliper adapter bracket (sold separately) depending on your motorcycle model.""",
    
    18: """High-flow synthetic media oil filter by K&N designed for extended engine life and superior protection. This premium filter features advanced synthetic fiber media that captures 99% of harmful contaminants while maintaining excellent oil flow. Provides better filtration than conventional paper filters. High-capacity design extends service intervals - can last up to 10,000 km between changes. Heavy-duty canister construction with 17mm hex nut for easy removal. Anti-drainback valve prevents dry starts. Silicone anti-drainback valve remains flexible in extreme temperatures. Compatible with conventional, synthetic, and synthetic blend motor oils. Fits most 100-200cc motorcycles (check fitment guide). Improves engine performance and longevity. Environmentally friendly with longer service life. Includes premium gasket for leak-free installation.""",
    
    19: """CNC-machined adjustable brake and clutch lever set by Rizoma. These premium levers feature 6-way span adjustment to accommodate different hand sizes and riding preferences. Manufactured from aerospace-grade aluminum with anodized finish in multiple colors (black, red, blue, gold). Ergonomic design reduces hand fatigue on long rides. Foldable design prevents breakage in case of falls. Precision ball bearings ensure smooth operation. Laser-etched adjustment markings for easy setting. Includes adapters for universal fitment on most motorcycles with hydraulic brake and clutch systems. Easy installation with included hardware. Significantly improves lever feel and control. Adds premium, race-inspired look to your motorcycle. Available in short and long versions. Backed by manufacturer's lifetime warranty against defects.""",
    
    20: """Heavy-duty O-ring drive chain by DID (Daido Kogyo) - the world's leading chain manufacturer. This premium gold-colored chain features sealed O-ring design that retains factory lubrication for extended life and minimal maintenance. Constructed from high-tensile strength alloy steel with gold zinc coating for corrosion resistance. 428 pitch, 120 links - suitable for most 100-200cc motorcycles. Precision-manufactured with tight tolerances for smooth, quiet operation. O-rings prevent dirt and water ingress while keeping lubrication sealed inside. Provides 2-3 times longer life than non-O-ring chains. Includes master link with clip-type connector. Pre-stretched to minimize adjustment requirements. Recommended for both street and off-road use. Proper installation and regular tension adjustment required for maximum lifespan."""
}

# Connect to database
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = conn.cursor()

# Update each product
updated_count = 0
for product_id, description in product_descriptions.items():
    try:
        cursor.execute(
            "UPDATE products SET description = %s WHERE product_id = %s",
            (description, product_id)
        )
        updated_count += 1
        print(f"[OK] Updated Product ID {product_id}")
    except Exception as e:
        print(f"[ERROR] Error updating Product ID {product_id}: {e}")

conn.commit()
cursor.close()
conn.close()

print(f"\n{'='*80}")
print(f"SUCCESS: Updated {updated_count} product descriptions!")
print(f"{'='*80}\n")
print("Product descriptions are now detailed and specific to each item.")
print("They include:")
print("  • Technical specifications")
print("  • Material details")
print("  • Compatibility information")
print("  • Installation notes")
print("  • Performance benefits")
print("  • Warranty information")
print("  • Usage recommendations")
