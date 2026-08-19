#!/usr/bin/env python3
"""Resmî tam metin çekici — mevzuat.gov.tr konsolide metnini .md'ye yazar.

kaynaklar.yaml'daki her kaydın kaynaklar[] listesinde bir mevzuat.gov.tr
`mevzuat?MevzuatNo=..&MevzuatTur=..&MevzuatTertip=..` adresi varsa, o mevzuatın
FihristDetayIframe HTML'ini çeker, temiz metne çevirir ve ilgili .md dosyasının
<!-- METIN:BASLANGIC --> ... <!-- METIN:BITIS --> bloğuna yazıp metin_durumu'nu
tam-metin yapar. (SSL doğrulaması kapalı — mevzuat.gov.tr sertifika zinciri
varsayılan pakette güvenilmiyor.)

Kullanım:
    python3 scripts/cek_metin.py                # tüm uygun kayıtlar
    python3 scripts/cek_metin.py <id1> <id2>    # yalnız belirtilen id'ler
"""
from __future__ import annotations
import html, pathlib, re, ssl, sys, time, urllib.request
import yaml

KOK = pathlib.Path(__file__).resolve().parent.parent
KUTUK = KOK / "data" / "kaynaklar.yaml"
METIN_BLOK = re.compile(r"(<!-- METIN:BASLANGIC -->)(.*?)(<!-- METIN:BITIS -->)", re.S)
MURL = re.compile(r"MevzuatNo=(\d+)&MevzuatTur=\w+&MevzuatTertip=(\w+)")
# Kayıt türü -> iframe'in beklediği MevzuatTur kodu (arama API'sinin sayısal
# tur'u iframe ile uyuşmuyor; doğru metin için tür kayıttan türetilir).
TUR_KODU = {"kanun": "1", "cbk": "19", "yonetmelik": "7", "teblig": "9",
            "tarife": "9", "genel-sart": "9", "genelge": "9", "karar": "1"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def anlamli_kelimeler(baslik):
    return [w for w in re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]{6,}", baslik or "")][:6]

def getiframe(no, tur, tertip):
    url = f"https://www.mevzuat.gov.tr/anasayfa/MevzuatFihristDetayIframe?MevzuatTur={tur}&MevzuatNo={no}&MevzuatTertip={tertip}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=45, context=CTX).read().decode("utf-8", "replace")

def html2text(h: str) -> str:
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", h)
    h = re.sub(r"(?i)<li[^>]*>", "- ", h)
    h = re.sub(r"(?i)</td>\s*<td[^>]*>", "  |  ", h)
    h = re.sub(r"<[^>]+>", "", h)
    h = html.unescape(h)
    h = "\n".join(ln.rstrip() for ln in h.splitlines())
    h = re.sub(r"[ \t]+\n", "\n", h)
    h = re.sub(r"\n{3,}", "\n\n", h)
    return h.strip()

def hedef_mevzuat(kayit):
    adaylar = list(kayit.get("kaynaklar") or [])
    dog = kayit.get("dogrulama") or {}
    if dog.get("kaynak"):
        adaylar.append(dog["kaynak"])
    for k in adaylar:
        m = MURL.search(str(k))
        if m:
            no, tertip = m.groups()
            tur = TUR_KODU.get(kayit.get("tur"), "1")  # türü kayıttan türet
            return no, tur, tertip
    return None

def main():
    veri = yaml.safe_load(KUTUK.read_text(encoding="utf-8"))
    istenen = set(sys.argv[1:])
    ok = atla = hata = 0
    for kayit in veri["belgeler"]:
        if istenen and kayit["id"] not in istenen:
            continue
        hedef = hedef_mevzuat(kayit)
        if not hedef:
            atla += 1; continue
        yol = KOK / kayit["klasor"] / f"{kayit['id']}.md"
        if not yol.exists():
            atla += 1; continue
        no, tur, tertip = hedef
        try:
            metin = html2text(getiframe(no, tur, tertip))
            if len(metin) < 300:
                print(f"  ⚠ kısa/boş ({len(metin)}): {kayit['id']}"); atla += 1; continue
            kel = anlamli_kelimeler(kayit.get("baslik"))
            ust = metin.upper()
            if kel and not any(w.upper() in ust for w in kel):
                print(f"  ⚠ jenerik/alakasız sayfa, atlandı: {kayit['id']}"); atla += 1; continue
            baslik = f"> Kaynak: mevzuat.gov.tr (No {no}, Tür {tur}, Tertip {tertip}) — çekim: 2026-08-19. Resmî konsolide metin; değişiklik dipnotları `(Değişik/Ek/Mülga:RG-…)` biçimindedir.\n\n"
            icerik = yol.read_text(encoding="utf-8")
            icerik = icerik.replace("metin_durumu: iskelet", "metin_durumu: tam-metin", 1)
            yeni = METIN_BLOK.sub(lambda m: m.group(1) + "\n" + baslik + metin + "\n" + m.group(3), icerik, count=1)
            yol.write_text(yeni, encoding="utf-8")
            print(f"  ✓ {kayit['id']}  ({len(metin):,} karakter)")
            ok += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  ✗ {kayit['id']}: {type(e).__name__} {str(e)[:80]}"); hata += 1
    print(f"\nÇekilen: {ok} | atlanan: {atla} | hata: {hata}")

if __name__ == "__main__":
    raise SystemExit(main())
