#!/usr/bin/env python3
"""
Depo denetleyicisi.

Kontroller:
  1. Her .md dosyasının YAML künyesi var mı, ayrıştırılabiliyor mu?
  2. Zorunlu alanlar mevcut mu?
  3. id dosya adıyla eşleşiyor mu, depoda benzersiz mi?
  4. enum alanları (tur, durum, metin_durumu, dogrulama.durum) geçerli mi?
  5. oncelik 1|2|3 mü, kaynaklar en az bir https adres içeriyor mu?
  6. Tarih alanları YYYY-AA-GG biçiminde mi?
  7. dogrulama.durum=dogrulandi ise tarih+yontem dolu mu?
  8. metin_durumu=tam-metin ise METIN bloğu gerçekten dolu mu?
  9. Depo içi göreli bağlantılar kırık mı?
 10. data/kaynaklar.yaml'daki her kaydın dosyası var mı?

Çıkış kodu: hata varsa 1.
"""
from __future__ import annotations

import pathlib
import re
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML gerekli:  pip install pyyaml")

KOK = pathlib.Path(__file__).resolve().parent.parent
BELGELER = KOK / "belgeler"
KUTUK = KOK / "data" / "kaynaklar.yaml"

ZORUNLU = ["id", "baslik", "tur", "otorite", "durum", "brans", "etiketler",
           "oncelik", "kaynaklar", "metin_durumu", "dogrulama", "son_guncelleme", "dil"]

TURLER = {"kanun", "cbk", "yonetmelik", "teblig", "tarife", "genel-sart", "genelge",
          "sektor-duyurusu", "bildirge", "rehber", "karar", "kurum", "koleksiyon", "rapor"}
DURUMLAR = {"yururlukte", "mulga", "kismen-iptal", "degisiklik-bekliyor", "bilinmiyor"}
METIN_DURUMLARI = {"iskelet", "ozet", "tam-metin"}
DOGRULAMA_DURUMLARI = {"dogrulandi", "dogrulanmadi"}

TARIH_DESENI = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BAG_DESENI = re.compile(r"\[[^\]]*\]\(([^)#][^)]*)\)")
METIN_BLOK = re.compile(r"<!-- METIN:BASLANGIC -->(.*?)<!-- METIN:BITIS -->", re.S)


def kunye_ayir(icerik: str):
    if not icerik.startswith("---"):
        return None, icerik
    parca = icerik.split("---", 2)
    if len(parca) < 3:
        return None, icerik
    try:
        return yaml.safe_load(parca[1]), parca[2]
    except yaml.YAMLError as hata:
        return {"__yaml_hatasi__": str(hata)}, parca[2]


def tarih_kontrol(deger, etiket: str, hatalar: list[str]) -> None:
    if deger in (None, "", "null"):
        return
    if not TARIH_DESENI.match(str(deger)):
        hatalar.append(f"{etiket} ISO 8601 (YYYY-AA-GG) değil: {deger!r}")


def dosya_denetle(yol: pathlib.Path, gorulen_id: dict[str, pathlib.Path]) -> list[str]:
    hatalar: list[str] = []
    icerik = yol.read_text(encoding="utf-8")
    kunye, govde = kunye_ayir(icerik)
    goreli = yol.relative_to(KOK)

    if kunye is None:
        return [f"{goreli}: YAML künye bloğu yok"]
    if "__yaml_hatasi__" in kunye:
        return [f"{goreli}: YAML ayrıştırılamadı — {kunye['__yaml_hatasi__']}"]

    for alan in ZORUNLU:
        if alan not in kunye or kunye[alan] in (None, "", []):
            hatalar.append(f"{goreli}: zorunlu alan eksik/boş → {alan}")

    kimlik = kunye.get("id")
    if kimlik:
        if kimlik != yol.stem:
            hatalar.append(f"{goreli}: id ({kimlik}) dosya adıyla ({yol.stem}) uyuşmuyor")
        if kimlik in gorulen_id:
            hatalar.append(f"{goreli}: id tekrar ediyor → {gorulen_id[kimlik]}")
        else:
            gorulen_id[kimlik] = goreli

    if kunye.get("tur") not in TURLER:
        hatalar.append(f"{goreli}: geçersiz tur → {kunye.get('tur')!r}")
    if kunye.get("durum") not in DURUMLAR:
        hatalar.append(f"{goreli}: geçersiz durum → {kunye.get('durum')!r}")
    if kunye.get("metin_durumu") not in METIN_DURUMLARI:
        hatalar.append(f"{goreli}: geçersiz metin_durumu → {kunye.get('metin_durumu')!r}")
    if kunye.get("oncelik") not in (1, 2, 3):
        hatalar.append(f"{goreli}: oncelik 1|2|3 olmalı → {kunye.get('oncelik')!r}")

    kaynaklar = kunye.get("kaynaklar") or []
    if not any(str(k).startswith("https://") for k in kaynaklar):
        hatalar.append(f"{goreli}: en az bir https:// kaynak adresi gerekli")

    rg = kunye.get("resmi_gazete") or {}
    if isinstance(rg, dict):
        tarih_kontrol(rg.get("tarih"), f"{goreli}: resmi_gazete.tarih", hatalar)
    tarih_kontrol(kunye.get("son_guncelleme"), f"{goreli}: son_guncelleme", hatalar)

    dog = kunye.get("dogrulama") or {}
    if not isinstance(dog, dict) or dog.get("durum") not in DOGRULAMA_DURUMLARI:
        hatalar.append(f"{goreli}: geçersiz dogrulama.durum → {dog.get('durum') if isinstance(dog, dict) else dog!r}")
    elif dog.get("durum") == "dogrulandi":
        if not dog.get("tarih"):
            hatalar.append(f"{goreli}: dogrulandi ise dogrulama.tarih (erişim tarihi) zorunlu")
        else:
            tarih_kontrol(dog.get("tarih"), f"{goreli}: dogrulama.tarih", hatalar)
        if not dog.get("yontem"):
            hatalar.append(f"{goreli}: dogrulandi ise dogrulama.yontem zorunlu")
        if not str(dog.get("kaynak") or "").startswith("https://"):
            hatalar.append(f"{goreli}: dogrulandi ise dogrulama.kaynak (resmî kurum URL'si) zorunlu")

    if kunye.get("metin_durumu") == "tam-metin":
        eslesme = METIN_BLOK.search(govde)
        govde_metni = (eslesme.group(1).strip() if eslesme else "")
        if len(govde_metni) < 200 or govde_metni.startswith("_Resmî metin henüz eklenmedi._"):
            hatalar.append(f"{goreli}: metin_durumu=tam-metin ama METIN bloğu boş/yetersiz")

    for bag in BAG_DESENI.findall(govde):
        if bag.startswith(("http://", "https://", "mailto:")):
            continue
        hedef = (yol.parent / bag.split("#")[0]).resolve()
        if not hedef.exists():
            hatalar.append(f"{goreli}: kırık iç bağlantı → {bag}")

    return hatalar


def main() -> int:
    hatalar: list[str] = []
    gorulen_id: dict[str, pathlib.Path] = {}

    dosyalar = sorted(BELGELER.rglob("*.md"))
    if not dosyalar:
        hatalar.append("belgeler/ altında .md dosyası yok")

    for yol in dosyalar:
        hatalar.extend(dosya_denetle(yol, gorulen_id))

    if KUTUK.exists():
        veri = yaml.safe_load(KUTUK.read_text(encoding="utf-8"))
        for kayit in veri.get("belgeler", []):
            beklenen = KOK / kayit["klasor"] / f"{kayit['id']}.md"
            if not beklenen.exists():
                hatalar.append(f"kütükte var, dosyası yok → {beklenen.relative_to(KOK)} "
                               f"(çözüm: python3 scripts/uret.py)")
    else:
        hatalar.append("data/kaynaklar.yaml bulunamadı")

    ozet: dict[str, int] = defaultdict(int)
    for yol in dosyalar:
        kunye, _ = kunye_ayir(yol.read_text(encoding="utf-8"))
        if isinstance(kunye, dict):
            ozet[str(kunye.get("metin_durumu"))] += 1

    print(f"Denetlenen dosya: {len(dosyalar)}")
    print("Metin durumu dağılımı: " + ", ".join(f"{k}={v}" for k, v in sorted(ozet.items())))

    if hatalar:
        print(f"\n❌ {len(hatalar)} hata:\n")
        for h in hatalar:
            print(f"  - {h}")
        return 1
    print("\n✅ Tüm denetimler başarılı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
