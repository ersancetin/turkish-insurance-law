#!/usr/bin/env python3
"""OCR tam metin çekici — taranmış PDF'leri Apple Vision (ocrmac) ile okur.

metin_durumu=iskelet olan ve kaynaklar[]'da .pdf bulunan genelge/sektör
duyurusu/rehber/karar/genel-şart kayıtları için PDF'i indirir, her sayfayı
görüntüye çevirip ocrmac (Türkçe) ile OCR yapar ve .md'nin METIN bloğuna yazar.
fitz ile doğrudan metin çıkanları (dijital PDF) atlar — onlar cek_pdf.py işi.

Kullanım: python3 scripts/cek_ocr.py [id ...]
"""
from __future__ import annotations
import io, pathlib, re, ssl, sys, time, urllib.request
from urllib.parse import urlsplit, urlunsplit, quote
import fitz, yaml
from ocrmac import ocrmac
from PIL import Image

KOK = pathlib.Path(__file__).resolve().parent.parent
KUTUK = KOK / "data" / "kaynaklar.yaml"
METIN = re.compile(r"(<!-- METIN:BASLANGIC -->)(.*?)(<!-- METIN:BITIS -->)", re.S)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
TIPLER = {"genelge", "sektor-duyurusu", "rehber", "karar", "genel-sart", "teblig"}

def safe(u):
    s = urlsplit(u); return urlunsplit((s.scheme, s.netloc, quote(s.path, safe="/%:"), quote(s.query, safe="=&%"), ""))
def dl(u):
    return urllib.request.urlopen(urllib.request.Request(safe(u), headers={"User-Agent": "Mozilla/5.0"}), timeout=120, context=CTX).read()
def pdf_url(k):
    for x in k.get("kaynaklar") or []:
        if ".pdf" in str(x).lower():
            return str(x)
    return None
def ocr_pdf(b, maxpage=80):
    doc = fitz.open(stream=b, filetype="pdf")
    # Önce dijital metin var mı? (varsa OCR gereksiz — cek_pdf işi, atla)
    dj = "\n".join(p.get_text() for p in doc)
    if len(dj.strip()) > 400:
        doc.close(); return None
    parts = []
    for i, page in enumerate(doc):
        if i >= maxpage: break
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        res = ocrmac.OCR(img, language_preference=["tr-TR"]).recognize()
        parts.append("\n".join(r[0] for r in res))
    doc.close()
    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip()

def main():
    veri = yaml.safe_load(KUTUK.read_text(encoding="utf-8"))
    istenen = set(sys.argv[1:])
    ok = atla = hata = dij = 0
    kayitlar = [k for k in veri["belgeler"] if (not istenen or k["id"] in istenen)]
    for n, k in enumerate(kayitlar, 1):
        if k.get("tur") not in TIPLER:
            atla += 1; continue
        url = pdf_url(k); yol = KOK / k["klasor"] / f"{k['id']}.md"
        if not url or not yol.exists():
            atla += 1; continue
        ic = yol.read_text(encoding="utf-8")
        if re.search(r"^metin_durumu: tam-metin", ic, re.M):
            atla += 1; continue
        try:
            metin = ocr_pdf(dl(url))
            if metin is None:
                dij += 1; continue  # dijital → cek_pdf işi
            if len(metin) < 120:
                atla += 1; continue
            bas = f"> Kaynak: {url} (SEDDK resmî PDF) — OCR ile çekildi (Apple Vision, tr): 2026-08-19.\n\n"
            yeni = ic.replace("metin_durumu: iskelet", "metin_durumu: tam-metin", 1)
            yeni = METIN.sub(lambda m: m.group(1) + "\n" + bas + metin + "\n" + m.group(3), yeni, count=1)
            yol.write_text(yeni, encoding="utf-8")
            ok += 1
            if ok % 25 == 0:
                print(f"[{n}/{len(kayitlar)}] OCR ok={ok} ({k['id']}, {len(metin)} kr)", flush=True)
            time.sleep(0.05)
        except Exception as e:
            hata += 1
            if hata <= 20:
                print(f"  ✗ {k['id']}: {type(e).__name__} {str(e)[:60]}", flush=True)
    print(f"\nOCR çekilen: {ok} | dijital(atlanan): {dij} | atlanan: {atla} | hata: {hata}", flush=True)

if __name__ == "__main__":
    raise SystemExit(main())
