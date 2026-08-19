#!/usr/bin/env python3
"""
Kaynak toplayıcı — resmî metinleri indirir ve Markdown'a çevirir.

Bu depo, dış ağ erişimi kısıtlı bir ortamda kuruldu; aşağıdaki alan adları
egress politikası tarafından engellendiği için metinler henüz çekilemedi:
    seddk.gov.tr · mevzuat.gov.tr · resmigazete.gov.tr · tsb.org.tr
    sigortatahkim.org · dask.gov.tr · tarsim.gov.tr · anayasa.gov.tr
Ağ erişimi olan bir ortamda bu betiği çalıştırın.

Kullanım:
    python3 scripts/cek.py --liste                 # toplanacak adresleri listele
    python3 scripts/cek.py --erisim-testi          # hangi alan adları açık, ölç
    python3 scripts/cek.py --oncelik 1             # P1 kayıtları indir + .md'ye yaz
    python3 scripts/cek.py --id gs-kasko           # tek kayıt
    python3 scripts/cek.py --oncelik 1 --sadece-indir   # yalnızca ham/ altına indir

Bağımlılık: yalnızca standart kütüphane. Varsa şunlar kullanılır:
    html2text (daha iyi HTML→MD), pdftotext (poppler-utils, PDF→metin)
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML gerekli:  pip install pyyaml")

KOK = pathlib.Path(__file__).resolve().parent.parent
KUTUK = KOK / "data" / "kaynaklar.yaml"
HAM = KOK / "ham"

KULLANICI_AJANI = (
    "Mozilla/5.0 (compatible; turkish-insurance-law-archiver/0.1; "
    "+https://github.com/ersancetin/turkish-insurance-law)"
)
BEKLEME_SN = 1.5  # aynı sunucuya art arda istek arası nezaket gecikmesi

ETIKET_SIL = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
BASLIK_DESENI = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.S | re.I)
ETIKET_DESENI = re.compile(r"<[^>]+>")


def kutuk_oku() -> dict:
    return yaml.safe_load(KUTUK.read_text(encoding="utf-8"))


def kayitlari_sec(veri: dict, args) -> list[dict]:
    kayitlar = veri["belgeler"]
    if args.id:
        kayitlar = [k for k in kayitlar if k["id"] in args.id]
    if args.oncelik:
        kayitlar = [k for k in kayitlar if k.get("oncelik", 3) <= args.oncelik]
    if args.tur:
        kayitlar = [k for k in kayitlar if k["tur"] in args.tur]
    return kayitlar


def alan_adi(url: str) -> str:
    return urllib.parse.urlparse(url).netloc


def indir(url: str, zaman_asimi: int = 30) -> tuple[bytes, str]:
    istek = urllib.request.Request(url, headers={"User-Agent": KULLANICI_AJANI})
    with urllib.request.urlopen(istek, timeout=zaman_asimi) as yanit:
        return yanit.read(), yanit.headers.get("Content-Type", "")


def html_to_md(ham_html: str) -> str:
    try:
        import html2text  # type: ignore

        cevirici = html2text.HTML2Text()
        cevirici.body_width = 0
        cevirici.ignore_images = True
        return cevirici.handle(ham_html)
    except ImportError:
        pass
    metin = ETIKET_SIL.sub("", ham_html)
    metin = BASLIK_DESENI.sub(lambda m: "\n\n" + "#" * int(m.group(1)) + " " + m.group(2) + "\n\n", metin)
    metin = re.sub(r"</(p|div|tr|li|br)>", "\n", metin, flags=re.I)
    metin = ETIKET_DESENI.sub("", metin)
    metin = html.unescape(metin)
    metin = re.sub(r"[ \t]+", " ", metin)
    metin = re.sub(r"\n{3,}", "\n\n", metin)
    return metin.strip()


def pdf_to_md(yol: pathlib.Path) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    cikti = yol.with_suffix(".txt")
    subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(yol), str(cikti)], check=True)
    metin = cikti.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\n{3,}", "\n\n", metin).strip()


def md_dosyasina_yaz(kayit: dict, metin: str, kaynak_url: str) -> bool:
    yol = KOK / kayit["klasor"] / f"{kayit['id']}.md"
    if not yol.exists():
        print(f"  ! hedef dosya yok: {yol.relative_to(KOK)} (önce scripts/uret.py)")
        return False
    icerik = yol.read_text(encoding="utf-8")
    blok = re.compile(r"(<!-- METIN:BASLANGIC -->)(.*?)(<!-- METIN:BITIS -->)", re.S)
    if not blok.search(icerik):
        print(f"  ! METIN bloğu bulunamadı: {yol.relative_to(KOK)}")
        return False
    yeni_govde = (
        f"\n\n> Kaynak: <{kaynak_url}> — otomatik dönüştürüldü, **elle gözden geçirilmelidir**.\n\n"
        f"{metin}\n\n"
    )
    icerik = blok.sub(lambda m: m.group(1) + yeni_govde + m.group(3), icerik)
    icerik = re.sub(r"^metin_durumu: .*$", "metin_durumu: tam-metin", icerik, count=1, flags=re.M)
    yol.write_text(icerik, encoding="utf-8")
    return True


def erisim_testi(veri: dict) -> int:
    adresler = {alan_adi(u) for k in veri["belgeler"] for u in (k.get("kaynaklar") or [])}
    adresler |= {alan_adi(u) for u in veri.get("portallar", {}).values()}
    print(f"{len(adresler)} alan adı test ediliyor…\n")
    acik, kapali = [], []
    for ad in sorted(adresler):
        if not ad:
            continue
        try:
            indir(f"https://{ad}/", zaman_asimi=15)
            acik.append(ad)
            print(f"  ✅ {ad}")
        except Exception as hata:  # noqa: BLE001
            kapali.append((ad, type(hata).__name__))
            print(f"  ⛔ {ad} — {type(hata).__name__}")
    print(f"\nAçık: {len(acik)} · Kapalı: {len(kapali)}")
    if kapali:
        print("\nErişim izni istenecek alan adları:")
        for ad, _ in kapali:
            print(f"  {ad}")
    return 0 if not kapali else 2


def liste(kayitlar: list[dict]) -> int:
    gruplu: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for k in kayitlar:
        for u in k.get("kaynaklar") or []:
            gruplu[alan_adi(u)].append((k["id"], u))
    toplam = sum(len(v) for v in gruplu.values())
    print(f"{len(kayitlar)} kayıt · {toplam} kaynak adresi · {len(gruplu)} alan adı\n")
    for ad in sorted(gruplu, key=lambda a: -len(gruplu[a])):
        print(f"## {ad}  ({len(gruplu[ad])} adres)")
        for kimlik, url in sorted(gruplu[ad]):
            print(f"  [{kimlik}] {url}")
        print()
    print("Öncelik dağılımı:", dict(Counter(k.get("oncelik", 3) for k in kayitlar)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Resmî metinleri indirir ve Markdown'a çevirir.")
    ap.add_argument("--liste", action="store_true", help="indirmeden adresleri listele")
    ap.add_argument("--erisim-testi", action="store_true", help="alan adlarına erişimi ölç")
    ap.add_argument("--oncelik", type=int, choices=[1, 2, 3], help="bu öncelik ve üstünü al")
    ap.add_argument("--id", nargs="*", help="yalnızca bu kayıt kimlikleri")
    ap.add_argument("--tur", nargs="*", help="yalnızca bu belge türleri")
    ap.add_argument("--sadece-indir", action="store_true", help="ham/ altına indir, .md'ye yazma")
    ap.add_argument("--bekleme", type=float, default=BEKLEME_SN, help="istekler arası saniye")
    args = ap.parse_args()

    veri = kutuk_oku()
    if args.erisim_testi:
        return erisim_testi(veri)

    kayitlar = kayitlari_sec(veri, args)
    if args.liste:
        return liste(kayitlar)
    if not (args.oncelik or args.id or args.tur):
        ap.error("indirme için --oncelik, --id veya --tur verin (ya da --liste kullanın)")

    HAM.mkdir(exist_ok=True)
    basarili = basarisiz = 0
    for kayit in kayitlar:
        kaynaklar = [u for u in (kayit.get("kaynaklar") or []) if u.startswith("https://")]
        if not kaynaklar:
            continue
        print(f"\n▶ {kayit['id']} — {kayit['baslik'][:70]}")
        for url in kaynaklar:
            try:
                veri_bayt, tur = indir(url)
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as hata:
                print(f"  ⛔ {url} — {hata}")
                continue
            finally:
                time.sleep(args.bekleme)

            hedef_dizin = HAM / kayit["id"]
            hedef_dizin.mkdir(parents=True, exist_ok=True)
            ad = pathlib.Path(urllib.parse.urlparse(url).path).name or "index.html"
            pdf_mi = "pdf" in tur.lower() or ad.lower().endswith(".pdf")
            ham_yol = hedef_dizin / (ad if "." in ad else ad + (".pdf" if pdf_mi else ".html"))
            ham_yol.write_bytes(veri_bayt)
            print(f"  ⬇ {url} → ham/{kayit['id']}/{ham_yol.name}")

            if args.sadece_indir:
                basarili += 1
                continue

            metin = pdf_to_md(ham_yol) if pdf_mi else html_to_md(veri_bayt.decode("utf-8", "replace"))
            if not metin:
                print("  ! metin çıkarılamadı (PDF için poppler-utils/pdftotext kurun)")
                basarisiz += 1
                continue
            if md_dosyasina_yaz(kayit, metin, url):
                print(f"  ✅ {kayit['klasor']}/{kayit['id']}.md güncellendi ({len(metin)} karakter)")
                basarili += 1
                break
        else:
            basarisiz += 1

    print(f"\nBaşarılı: {basarili} · Başarısız: {basarisiz}")
    print("Sonraki adım: python3 scripts/dogrula.py  ve künyeleri elle doğrulayın.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
