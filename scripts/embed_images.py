#!/usr/bin/env python3
"""
Embed product photos into favorit-impulse-500.html so they show everywhere
(Claude artifact, email, offline). Run on your own computer:

    python3 embed_images.py favorit-impulse-500.html

Output: favorit-impulse-500-with-photos.html next to the input file.
Optional but recommended (shrinks photos so the file stays under ~12 MB):
    pip3 install pillow
"""
import base64, io, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_PX, QUALITY, WORKERS = 360, 72, 8
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
REFERER = {"img.fix-price.com": "https://fix-price.com/", "img.fix-price.kz": "https://fix-price.kz/",
           "asset.action.com": "https://www.action.com/", "n11scdn.akamaized.net": "https://www.n11.com/",
           "resources.cdn-kaspi.kz": "https://kaspi.kz/", "s.f.kz": "https://www.flip.kz/"}

try:
    from PIL import Image
except ImportError:
    Image = None
    print("Pillow not installed: photos will be embedded at full size (bigger file).")

def fetch(url):
    host = urlparse(url).netloc
    headers = {"User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"}
    if host in REFERER:
        headers["Referer"] = REFERER[host]
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=25) as r:
                return r.read(), r.headers.get_content_type()
        except Exception as e:
            err = e
            time.sleep(1.5 * (attempt + 1))
    raise err

def to_data_uri(url):
    raw, ctype = fetch(url)
    if Image:
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGBA") if im.mode in ("P", "LA") else im
        if im.mode == "RGBA":                      # flatten transparency onto white
            bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
        im = im.convert("RGB"); im.thumbnail((MAX_PX, MAX_PX))
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=QUALITY, optimize=True)
        raw, ctype = buf.getvalue(), "image/jpeg"
    return f"data:{ctype};base64,{base64.b64encode(raw).decode()}"

def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "favorit-impulse-500.html")
    html = src.read_text(encoding="utf-8")
    m = re.search(r"const DATA = (\[.*?\]);\n", html, re.S)
    if not m:
        sys.exit("Could not find the product data in the HTML.")
    data = json.loads(m.group(1))
    urls = sorted({d["img"] for d in data if d["img"].startswith("http")})
    print(f"Downloading {len(urls)} photos...")
    done, failed = {}, []
    def job(u):
        try:
            done[u] = to_data_uri(u)
        except Exception as e:
            failed.append((u, str(e)[:80]))
        n = len(done) + len(failed)
        if n % 50 == 0 or n == len(urls):
            print(f"  {n}/{len(urls)}  ok={len(done)} failed={len(failed)}")
    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(job, urls))
    photos = src.with_name("photos"); photos.mkdir(exist_ok=True)
    for d in data:
        uri = done.get(d["img"])
        if uri:
            ext = "jpg" if "jpeg" in uri[:30] else uri[11:uri.index(";")].split("/")[-1]
            slug = re.sub(r"[^a-z0-9]+", "-", d["l5"].lower()).strip("-")[:50]
            (photos / f"{d['rank']:03d}_{slug}.{ext}").write_bytes(base64.b64decode(uri.split(",",1)[1]))
            d["img"] = uri                             # failed ones keep the web link
    new_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = html[:m.start(1)] + new_json + html[m.end(1):]
    dst = src.with_name(src.stem + "-with-photos.html")
    dst.write_text(out, encoding="utf-8")
    print(f"\nPhotos saved in {photos}/")
    print(f"Saved {dst}  ({dst.stat().st_size/1e6:.1f} MB)  embedded {len(done)}, failed {len(failed)}")
    if failed:
        print("Failed (these cards keep the web link):")
        for u, e in failed[:20]:
            print("  ", u, "->", e)

if __name__ == "__main__":
    main()
