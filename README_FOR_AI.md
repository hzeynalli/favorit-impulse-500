# Favorit Impulse 500 — handover package

## What this is
Italdizain (Baku home & tableware retailer) runs a ~500-SKU home & kitchen corner inside a Baku supermarket. This package is the evidence-ranked list of the **500 Level-5 product categories** to stock there, each with one concrete example product (name, link, photo link, benchmark price), and the proof behind each rank.

## Your job (the one thing left)
Add the product photos. Everything else is done.

1. Run: `python3 scripts/favorit_with_photos.py` (from any folder; plain Python 3 is enough, Pillow optional).
   - It contains the whole page. It downloads the 500 photos, shrinks them, and writes:
     - `favorit-impulse-500-with-photos.html` — the finished page with photos embedded (target < 16 MB).
     - `photos/<rank>_<l5>.jpg` — every photo as a file.
   - It sends a normal browser User-Agent and the retailer's own site as Referer, retries 3 times, and keeps the web link for any photo that fails. It prints a list of failures at the end.
2. If some photos fail: open the product page (`data/image_manifest.csv` has product_url), take its main product image, and re-run or patch the `img` field in the JSON inside the HTML. Do NOT substitute a different product.
3. Return `favorit-impulse-500-with-photos.html` to the user (Huseyn). If a PDF is wanted, print that HTML to PDF (A4 landscape, background graphics on) or build a PDF from `data/favorit_500.json` + `photos/`.

Do not change ranks, scores, categories, prices or evidence — they are the research result.

## Files
- `app/favorit-impulse-500.html` — the interactive page (filters, search, table view, CSV export). Photos are web links here, so they only show where the browser may load them.
- `data/favorit_500.json` / `.csv` — the 500 rows. Key fields: rank, score, tier, l1–l5, name, retailer, country, price + cur (local), azn, rk (bestseller ranks: chain, rank, category, listing URL, sort), reviews, countries, url (product page), img (photo URL), ev (evidence text).
- `data/favorit_all_candidates.json` — all 642 candidates incl. the 142 below the cut.
- `data/image_manifest.csv` — rank, L5, suggested filename, image URL, product URL.
- `evidence/sweeps/` — the 3,527 ranked listing records (Carrefour PL "most popular", Fix Price RU sorted by units sold, Fix Price KZ "popular first", n11 TR best-selling) and the category pages swept.
- `evidence/round1/` — the first research round (presence in Fix Price, Action, n11, Kaspi, Flip.kz etc., with review counts).
- `scripts/embed_images.py` — same photo step for any copy of the HTML: `python3 embed_images.py app/favorit-impulse-500.html`.

## Method (short)
- Benchmarks: Kazakhstan, Turkey, Poland, Russia (no Azerbaijani sources). Research 24–25 Sep 2026. Prices converted to AZN at CBAR rates of 24.09.2026 (PLN 0.442, RUB 0.020073, TRY 0.0348, KZT 0.003815).
- Score 0–100 = bestseller rank 45 (per chain: top10 100%, top24 90%, top60 75%, top120 60%, deeper 45%; Carrefour ×1.25 as the supermarket channel; two strong chains = full marks; categories under 30 items capped at 60%) + breadth of countries 15 + n11 buyer reviews 15 (log, full at 2,500) + impulse price 25 (≤5 AZN 100%, ≤10 85%, ≤17 60%, ≤25 30%, above 10%).
- Excluded by the client: stationery, gift, party, outdoor, seasonal, kids, pets, personal. Also excluded: food, chemicals, paper/film consumables, furniture, big appliances, pro tools.
- Limits: chain-wide online rankings, not single-store sell-through; Carrefour's "most popular" may include page views; some material matches (plates, bowls, boards) were made from names.
