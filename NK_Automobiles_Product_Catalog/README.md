# NK Automobiles — 160-product catalog starter

## Contents
- `products.csv`: spreadsheet-ready product catalogue (160 rows).
- `products.json`: same data for API/database import.
- `images/<category>/`: 160 uniquely named SVG placeholder assets, one per product.
- `SOURCES_AND_VERIFICATION.md`: source notes and Hubballi quote workflow.
- `preview.html`: local browser preview of the first 16 products.

## Important image note
The included SVGs are labelled placeholders, not photographs of actual spare parts. They exist so each product has a unique, correctly named asset path for wiring up the website. Replace them with licensed real product photos or your own photographs before publishing product cards as real inventory. Do not present placeholder illustrations as actual products.

## Pricing note
This starter catalog intentionally does not invent local Hubballi prices. Three entries contain online listing references and are marked as not verified in Hubballi. All other products have blank `price_inr` and `HUBBALLI_QUOTE_REQUIRED` status. Get a dated quote from a local shop or authorized dealer, record whether the item is OEM or aftermarket, and update `price_inr`, `price_source`, `source_url`, and `price_status`.

## Compatibility note
The eight requested models are listed as the target range, but this does not mean every part fits every model. For most entries, compatibility must be verified by model year, variant, brake type, engine code, dimensions and/or OEM part number before purchase or sale. Only product listings explicitly mentioned in `compatible_models` are treated as narrower matches.

## Suggested database fields
Use `product_id` as a stable ID. Store price as a numeric INR value (not a formatted string), image path as a relative path, and price/fitment verification status separately. Avoid displaying blank prices as ₹0; display “Price on request” until a quote is verified.
