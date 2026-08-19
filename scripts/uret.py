#!/usr/bin/env python3
"""
Türk Sigorta Hukuku deposu — belge üreticisi.

data/kaynaklar.yaml dosyasını okuyup:
  1. belgeler/** altında her kayıt için bir .md iskeleti üretir (varsa dokunmaz),
  2. data/kaynaklar.json (makine okunur kütük) yazar,
  3. INDEX.md (ana dizin) üretir,
  4. meta/durum-raporu.md (kapsam/ilerleme raporu) üretir.

Kullanım:
    python3 scripts/uret.py            # eksikleri üret, mevcut .md'lere dokunma
    python3 scripts/uret.py --force    # tüm iskeletleri yeniden yaz (İÇERİK KAYBEDER)
    python3 scripts/uret.py --kontrol  # hiçbir şey yazma, sadece farkı raporla
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML gerekli:  pip install pyyaml")

KOK = pathlib.Path(__file__).resolve().parent.parent
KUTUK = KOK / "data" / "kaynaklar.yaml"

TUR_ETIKET = {
    "kanun": "Kanun",
    "cbk": "Cumhurbaşkanlığı Kararnamesi",
    "yonetmelik": "Yönetmelik",
    "teblig": "Tebliğ",
    "tarife": "Tarife / Talimat",
    "genel-sart": "Genel Şart",
    "genelge": "Genelge",
    "sektor-duyurusu": "Sektör Duyurusu",
    "bildirge": "Bildirge / İlke Kararı",
    "rehber": "Rehber",
    "karar": "Yargı Kararı",
    "kurum": "Kurum Dosyası",
    "koleksiyon": "Koleksiyon (seri toplama görevi)",
    "rapor": "Rapor",
}

DURUM_ETIKET = {
    "yururlukte": "Yürürlükte",
    "mulga": "Mülga",
    "kismen-iptal": "Kısmen iptal edilmiş",
    "degisiklik-bekliyor": "Yakın tarihli değişiklik içeriyor",
    "bilinmiyor": "Bilinmiyor",
}


def kutugu_oku() -> dict:
    with KUTUK.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def yml_liste(deger) -> str:
    if not deger:
        return "[]"
    return "[" + ", ".join(str(x) for x in deger) + "]"


def frontmatter(kayit: dict, guncelleme: str) -> str:
    kaynaklar = "\n".join(f'  - "{k}"' for k in kayit.get("kaynaklar") or []) or "  []"
    numara = f'"{kayit["numara"]}"' if kayit.get("numara") else "null"
    rg_t = f'"{kayit["rg_tarihi"]}"' if kayit.get("rg_tarihi") else "null"
    rg_s = f'"{kayit["rg_sayisi"]}"' if kayit.get("rg_sayisi") else "null"
    dog = kayit.get("dogrulama") or {}
    dog_durum = dog.get("durum", "dogrulanmadi")
    dog_tarih = f'"{dog["tarih"]}"' if dog.get("tarih") else "null"
    dog_yontem = f'"{dog["yontem"]}"' if dog.get("yontem") else "null"
    return f"""---
id: {kayit['id']}
baslik: "{kayit['baslik']}"
tur: {kayit['tur']}
tur_etiket: "{TUR_ETIKET.get(kayit['tur'], kayit['tur'])}"
otorite: "{kayit.get('otorite') or ''}"
numara: {numara}
resmi_gazete:
  tarih: {rg_t}
  sayi: {rg_s}
durum: {kayit.get('durum', 'bilinmiyor')}
brans: {yml_liste(kayit.get('brans'))}
etiketler: {yml_liste(kayit.get('etiketler'))}
oncelik: {kayit.get('oncelik', 3)}
kaynaklar:
{kaynaklar}
metin_durumu: iskelet
dogrulama:
  durum: {dog_durum}
  tarih: {dog_tarih}
  yontem: {dog_yontem}
son_guncelleme: "{guncelleme}"
dil: tr
lisans: "Resmî mevzuat metinleri 5846 s. FSEK m.31 uyarınca serbesttir; bu dosyadaki derleme ve notlar CC BY 4.0"
---"""


def govde(kayit: dict) -> str:
    kaynak_satirlari = "\n".join(f"- <{k}>" for k in kayit.get("kaynaklar") or []) or "- _Kaynak adresi eklenmedi._"
    seri = kayit.get("seri")
    seri_blok = ""
    if seri:
        satirlar = ["\n## Seri bilgisi\n"]
        if seri.get("numara_deseni"):
            satirlar.append(f"- **Numara deseni:** `{seri['numara_deseni']}`")
        if seri.get("onceki_otorite"):
            satirlar.append(f"- **Önceki otorite:** {seri['onceki_otorite']}")
        for ornek in seri.get("bilinen_ornekler") or []:
            satirlar.append(f"- **Bilinen örnek:** {ornek}")
        seri_blok = "\n".join(satirlar) + "\n"

    dog = kayit.get("dogrulama") or {}
    if dog.get("durum") == "dogrulandi":
        uyari = (
            "> [!NOTE]\n"
            f"> **Künye doğrulandı** ({dog.get('tarih')}). Resmî Gazete tarih ve sayısı "
            "resmî kaynaktan teyit edilmiştir.\n"
            "> Ancak **tam metin henüz eklenmemiştir** (`metin_durumu: iskelet`); madde metinleri "
            "için aşağıdaki resmî kaynağa başvurun."
        )
        dog_satiri = f"| Doğrulama | ✅ Künye doğrulandı ({dog.get('tarih')}) |"
    else:
        uyari = (
            "> [!WARNING]\n"
            "> **Bu dosya bir iskelettir.** Resmî metin henüz eklenmemiştir ve künye bilgileri\n"
            "> (Resmî Gazete tarih/sayı, yürürlük durumu) **doğrulanmamıştır**.\n"
            "> Hukuki işlem yapmadan önce aşağıdaki resmî kaynaktan teyit edin.\n"
            "> Doldurma adımları için bkz. `KATKI-REHBERI.md`."
        )
        dog_satiri = "| Doğrulama | ⛔ Doğrulanmadı |"

    return f"""
# {kayit['baslik']}

{uyari}

## Künye

| Alan | Değer |
| --- | --- |
| Belge türü | {TUR_ETIKET.get(kayit['tur'], kayit['tur'])} |
| Otorite | {kayit.get('otorite') or '—'} |
| Numara | {kayit.get('numara') or '—'} |
| Resmî Gazete | {kayit.get('rg_tarihi') or '—'} / {kayit.get('rg_sayisi') or '—'} |
| Durum | {DURUM_ETIKET.get(kayit.get('durum'), kayit.get('durum'))} |
{dog_satiri}
| Branş | {', '.join(kayit.get('brans') or []) or '—'} |
| Öncelik | {kayit.get('oncelik', 3)} |

## Özet

{kayit.get('ozet', '_Özet girilmedi._')}
{seri_blok}
## Resmî metin

<!-- METIN:BASLANGIC -->
_Resmî metin henüz eklenmedi._

Metni eklerken:
1. Aşağıdaki resmî kaynaktan tam metni alın (mümkünse konsolide/güncel hâli).
2. Madde başlıklarını `## Madde N — Başlık` düzeninde işaretleyin.
3. Değişiklik dipnotlarını maddenin altında `> Değişiklik:` satırı olarak koruyun.
4. Frontmatter'da `metin_durumu: tam-metin` ve `dogrulama.durum: dogrulandi` yapın.
<!-- METIN:BITIS -->

## Değişiklik geçmişi

| Tarih | RG sayısı | Değişikliğin konusu | Not |
| --- | --- | --- | --- |
| — | — | — | _Doldurulacak_ |

## İlgili belgeler

- _Bu belgeyle birlikte okunması gereken kayıtlar `data/kaynaklar.yaml` etiketleri üzerinden eşleştirilir._

## Resmî kaynaklar

{kaynak_satirlari}

## Notlar

- _Uygulama notları, içtihat atıfları ve tartışmalı noktalar buraya._
"""


def dosya_yolu(kayit: dict) -> pathlib.Path:
    return KOK / kayit["klasor"] / f"{kayit['id']}.md"


def index_uret(veri: dict) -> str:
    belgeler = veri["belgeler"]
    gruplu: dict[str, list[dict]] = defaultdict(list)
    for k in belgeler:
        gruplu[k["klasor"]].append(k)

    satirlar = [
        "# İçindekiler — Türk Sigorta Hukuku Kaynak Deposu",
        "",
        "> Bu dosya `scripts/uret.py` tarafından **otomatik üretilir**. Elle düzenlemeyin;",
        "> değişiklik için `data/kaynaklar.yaml` dosyasını güncelleyip betiği yeniden çalıştırın.",
        "",
        f"**Toplam kayıt:** {len(belgeler)}  |  **Kütük sürümü:** {veri.get('surum')}  |  **Güncelleme:** {veri.get('guncelleme')}",
        "",
        "Durum rozetleri: ✅ yürürlükte · ⚠️ kısmen iptal · 🔄 yakın değişiklik · ⛔ mülga · ❔ bilinmiyor",
        "",
    ]
    rozet = {
        "yururlukte": "✅",
        "kismen-iptal": "⚠️",
        "degisiklik-bekliyor": "🔄",
        "mulga": "⛔",
        "bilinmiyor": "❔",
    }
    for klasor in sorted(gruplu):
        satirlar.append(f"## `{klasor}`")
        satirlar.append("")
        satirlar.append("| # | Belge | Tür | Durum | Öncelik |")
        satirlar.append("| --- | --- | --- | --- | --- |")
        for i, k in enumerate(sorted(gruplu[klasor], key=lambda x: (x.get("oncelik", 3), x["baslik"])), 1):
            yol = f"{k['klasor']}/{k['id']}.md"
            satirlar.append(
                f"| {i} | [{k['baslik']}]({yol}) | {TUR_ETIKET.get(k['tur'], k['tur'])} "
                f"| {rozet.get(k.get('durum'), '❔')} | P{k.get('oncelik', 3)} |"
            )
        satirlar.append("")
    return "\n".join(satirlar) + "\n"


def durum_raporu_uret(veri: dict) -> str:
    belgeler = veri["belgeler"]
    tur_sayim = Counter(k["tur"] for k in belgeler)
    durum_sayim = Counter(k.get("durum", "bilinmiyor") for k in belgeler)
    oncelik_sayim = Counter(k.get("oncelik", 3) for k in belgeler)
    rg_eksik = [k for k in belgeler if not k.get("rg_tarihi") and k["tur"] in {"kanun", "cbk", "yonetmelik", "genel-sart", "teblig"}]

    satirlar = [
        "# Durum Raporu",
        "",
        "> Otomatik üretilir (`scripts/uret.py`). Deponun kapsam ve tamamlanma durumunu gösterir.",
        "",
        f"- **Kütükteki kayıt sayısı:** {len(belgeler)}",
        "- **Tam metin eklenmiş belge sayısı:** dosyaların `metin_durumu` alanından hesaplanır (aşağıdaki tabloya bakın).",
        "",
        "## Belge türüne göre dağılım",
        "",
        "| Tür | Adet |",
        "| --- | --- |",
    ]
    for tur, adet in tur_sayim.most_common():
        satirlar.append(f"| {TUR_ETIKET.get(tur, tur)} | {adet} |")

    satirlar += ["", "## Yürürlük durumu", "", "| Durum | Adet |", "| --- | --- |"]
    for durum, adet in durum_sayim.most_common():
        satirlar.append(f"| {DURUM_ETIKET.get(durum, durum)} | {adet} |")

    satirlar += ["", "## Toplama önceliği", "", "| Öncelik | Adet | Anlamı |", "| --- | --- | --- |"]
    anlam = {1: "Kritik — önce toplanacak", 2: "Önemli", 3: "Tamamlayıcı"}
    for onc in sorted(oncelik_sayim):
        satirlar.append(f"| P{onc} | {oncelik_sayim[onc]} | {anlam.get(onc, '')} |")

    satirlar += [
        "",
        "## Künyesi eksik kayıtlar (Resmî Gazete tarihi girilmemiş)",
        "",
        f"Toplam **{len(rg_eksik)}** kayıt. Resmî metin çekilirken bu alanlar doldurulmalıdır.",
        "",
    ]
    for k in sorted(rg_eksik, key=lambda x: x["id"]):
        satirlar.append(f"- `{k['id']}` — {k['baslik']}")

    dogrulanan = [k for k in belgeler if (k.get("dogrulama") or {}).get("durum") == "dogrulandi"]
    satirlar += [
        "",
        "## Künye doğrulama durumu",
        "",
        f"Resmî kaynaktan (Resmî Gazete / mevzuat.gov.tr / SEDDK) künyesi teyit edilmiş "
        f"**{len(dogrulanan)}** kayıt / toplam {len(belgeler)}.",
        "",
    ]
    if dogrulanan:
        satirlar += ["| Kayıt | Resmî Gazete | Doğrulama tarihi |", "| --- | --- | --- |"]
        for k in sorted(dogrulanan, key=lambda x: x["id"]):
            rg = f"{k.get('rg_tarihi') or '—'} / {k.get('rg_sayisi') or '—'}"
            tarih = (k.get("dogrulama") or {}).get("tarih") or "—"
            satirlar.append(f"| `{k['id']}` | {rg} | {tarih} |")
        satirlar.append("")

    satirlar += [
        "## Doğrulama uyarısı",
        "",
        veri.get("dogrulama_notu", "").strip(),
        "",
    ]
    return "\n".join(satirlar) + "\n"


def main() -> int:
    ayrist = argparse.ArgumentParser(description="Belge iskeletlerini ve dizinleri üretir.")
    ayrist.add_argument("--force", action="store_true", help="mevcut .md dosyalarının üzerine yaz")
    ayrist.add_argument("--kontrol", action="store_true", help="yazma, sadece raporla")
    args = ayrist.parse_args()

    veri = kutugu_oku()
    belgeler = veri["belgeler"]
    guncelleme = str(veri.get("guncelleme", ""))

    kimlikler = Counter(k["id"] for k in belgeler)
    tekrar = [i for i, c in kimlikler.items() if c > 1]
    if tekrar:
        sys.exit(f"HATA: tekrar eden id: {tekrar}")

    uretilen, atlanan = 0, 0
    for kayit in belgeler:
        yol = dosya_yolu(kayit)
        if yol.exists() and not args.force:
            atlanan += 1
            continue
        if args.kontrol:
            print(f"[eksik] {yol.relative_to(KOK)}")
            uretilen += 1
            continue
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(frontmatter(kayit, guncelleme) + govde(kayit), encoding="utf-8")
        uretilen += 1

    if not args.kontrol:
        (KOK / "data" / "kaynaklar.json").write_text(
            json.dumps(veri, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (KOK / "INDEX.md").write_text(index_uret(veri), encoding="utf-8")
        (KOK / "meta" / "durum-raporu.md").write_text(durum_raporu_uret(veri), encoding="utf-8")

    print(f"Kayıt: {len(belgeler)} | üretilen: {uretilen} | atlanan (mevcut): {atlanan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
