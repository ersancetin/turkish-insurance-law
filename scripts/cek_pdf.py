#!/usr/bin/env python3
"""PDF tam metin çekici — kaynaklar[].pdf'i indirip fitz ile metne çevirir.

metin_durumu=iskelet olan ve kaynaklar[]'da .pdf adresi bulunan kayıtlar için
(SEDDK genelge/duyuru, RG'siz klasik genel şartlar) PDF'i indirir, PyMuPDF ile
metni çıkarır ve .md'nin METIN bloğuna yazar. Başlık-alaka kontrolü ile hatalı/
alakasız PDF'ler elenir.

Kullanım: python3 scripts/cek_pdf.py [id1 id2 ...]
"""
from __future__ import annotations
import pathlib, re, ssl, sys, time, urllib.request
from urllib.parse import urlsplit, urlunsplit, quote
import fitz, yaml

KOK = pathlib.Path(__file__).resolve().parent.parent
KUTUK = KOK / "data" / "kaynaklar.yaml"
METIN_BLOK = re.compile(r"(<!-- METIN:BASLANGIC -->)(.*?)(<!-- METIN:BITIS -->)", re.S)
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def safe(u):
    # Zaten %-encoded yolları bozmadan yalnız boşluk/Türkçe karakteri encode et.
    s = urlsplit(u)
    return urlunsplit((s.scheme, s.netloc, quote(s.path, safe="/%:"), quote(s.query, safe="=&%"), ""))

def dl(url):
    req = urllib.request.Request(safe(url), headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=90, context=CTX).read()

def pdftext(b):
    doc = fitz.open(stream=b, filetype="pdf")
    t = "\n".join(p.get_text() for p in doc)
    doc.close()
    t = re.sub(r"[ \t]+\n", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def pdf_url(kayit):
    for k in kayit.get("kaynaklar") or []:
        if str(k).lower().endswith(".pdf") or ".pdf" in str(k).lower():
            return str(k)
    return None

def anlamli(baslik):
    return re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]{6,}", baslik or "")[:6]

def main():
    veri = yaml.safe_load(KUTUK.read_text(encoding="utf-8"))
    istenen = set(sys.argv[1:])
    ok = atla = hata = 0
    for kayit in veri["belgeler"]:
        if istenen and kayit["id"] not in istenen:
            continue
        url = pdf_url(kayit)
        yol = KOK / kayit["klasor"] / f"{kayit['id']}.md"
        if not url or not yol.exists():
            atla += 1; continue
        icerik0 = yol.read_text(encoding="utf-8")
        if re.search(r"^metin_durumu: tam-metin", icerik0, re.M):
            atla += 1; continue
        try:
            metin = pdftext(dl(url))
            if len(metin) < 300:
                atla += 1; continue
            kel = anlamli(kayit.get("baslik")); ust = metin.upper()
            if kel and not any(w.upper() in ust for w in kel):
                print(f"  ⚠ alakasız, atla: {kayit['id']}"); atla += 1; continue
            bas = f"> Kaynak: {url} (SEDDK/TSB resmî PDF) — çekim: 2026-08-19.\n\n"
            yeni = icerik0.replace("metin_durumu: iskelet", "metin_durumu: tam-metin", 1)
            yeni = METIN_BLOK.sub(lambda m: m.group(1) + "\n" + bas + metin + "\n" + m.group(3), yeni, count=1)
            yol.write_text(yeni, encoding="utf-8")
            print(f"  ✓ {kayit['id']} ({len(metin):,} kr)")
            ok += 1; time.sleep(0.2)
        except Exception as e:
            print(f"  ✗ {kayit['id']}: {type(e).__name__} {str(e)[:70]}"); hata += 1
    print(f"\nÇekilen: {ok} | atlanan: {atla} | hata: {hata}")

if __name__ == "__main__":
    raise SystemExit(main())
