# Sources and verification workflow

## Public source references checked on 23 October 2026
- Deep Automobiles — Hero Splendor Plus spare parts catalog and listed prices: https://www.deepautomobile.com/bike/hero/splendor-plus
- Jectec — India bike spare-parts catalog/reference guide: https://jectec.in/bike-spare-parts
- Parts My Bike — example product listing domain: https://partsmybike.com/
- Hero MotoCorp official site, for model-specific genuine parts/listing verification: https://www.heromotocorp.com/

Search results included an official Hero MotoCorp listing for a Splendor+ right rear-view mirror at ₹175 (listing title included part number 88110AAEH31S), a Parts My Bike listing for a Splendor-family gear shift shaft at ₹377, and a Bajaj chain-guide listing at ₹183. These are online listing references only, not a verified current Hubballi counter price. Check live pages, shipping, tax, model variant and stock before using them.

## Local Hubballi quote candidates (availability and price must be confirmed by calling)
- Banashree Automobiles, Banashakari Plaza, Kalidas Nagar, Hubballi 580031; phone 089042 67195.
- Jay Motorcycle Spares Hubli (Bajaj spares), Nehru Stadium Road / Koppikar Road, New Hubli 580020; phone +91 80888 84666.
- Naveen Automobiles, Shop 10, Sujata Sanjota Complex, near Old Bus Stand, Hubballi 580029; phone +91 96206 14585.
- Shantesha Honda, Royal Plaza, Sarvoday Circle, Keshwapur, Hubballi 580023; phone +91 73531 00073.
- Shree Jee Auto Point, Stall 27, Nehru Stadium, New Hubli 580020; phone +91 98802 43362 (accessories).

These businesses are local quote leads only; no product-specific inventory or price has been verified.

## Suggested quote fields to add
`quote_date`, `shop_name`, `shop_phone`, `quoted_price_inr`, `brand_type` (OEM/aftermarket), `part_number_confirmed`, `model_year_confirmed`, `stock_confirmed`, `quote_valid_until`.

## Price status values
- `ONLINE_LISTING_PRICE_NOT_HUBBALLI_VERIFIED`: an online listing was found; not a local quote.
- `HUBBALLI_QUOTE_REQUIRED`: no reliable product-specific current price was verified.
