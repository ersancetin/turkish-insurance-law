# YAML Künye (Frontmatter) Şeması

Her belge dosyası bir YAML künye bloğuyla başlar. Alanlar `scripts/dogrula.py`
tarafından denetlenir.

```yaml
---
id: gs-zmss-trafik                       # zorunlu · string · benzersiz · kebab-case
baslik: "…"                              # zorunlu · string · resmî tam ad
tur: genel-sart                          # zorunlu · enum · meta/taksonomi.md §1
tur_etiket: "Genel Şart"                 # üretilir · insan okuru için
otorite: "SEDDK"                         # zorunlu · string
numara: null                             # opsiyonel · string ("5684", "2025/28")
resmi_gazete:
  tarih: "2015-05-14"                    # opsiyonel · ISO 8601 (YYYY-AA-GG)
  sayi: "29355"                          # opsiyonel · string
durum: kismen-iptal                      # zorunlu · enum · §3 taksonomi
brans: [sorumluluk, motorlu-arac]        # zorunlu · liste · §2 taksonomi
etiketler: [zmss, trafik, deger-kaybi]   # zorunlu · liste
oncelik: 1                               # zorunlu · 1|2|3
kaynaklar:                               # zorunlu · en az 1 URL
  - "https://…"
metin_durumu: iskelet                    # zorunlu · iskelet|ozet|tam-metin
dogrulama:
  durum: dogrulanmadi                    # zorunlu · dogrulandi|dogrulanmadi
  tarih: null                            # dogrulandi ise zorunlu · ISO 8601
  yontem: null                           # dogrulandi ise zorunlu · nasıl teyit edildi
son_guncelleme: "2026-08-19"             # zorunlu · ISO 8601
dil: tr                                  # zorunlu · ISO 639-1
lisans: "…"                              # zorunlu
---
```

## Alan alan açıklama

| Alan | Neden var | Ajanın kullanımı |
| --- | --- | --- |
| `id` | Kararlı kimlik; dosya adı ve çapraz atıf | Belge çözümleme anahtarı |
| `baslik` | Resmî ad — atıfta kullanılır | Alıntı başlığı |
| `tur` | Normlar hiyerarşisindeki yeri | Çatışma çözümünde üstünlük sırası |
| `otorite` | Kim çıkardı | Yetki denetimi, atıf |
| `resmi_gazete` | Künye | Atıfta zorunlu; `dogrulama` ile birlikte okunur |
| `durum` | Yürürlük | ⚠️ İptal/mülga uyarısı üretmek için |
| `brans` / `etiketler` | Arama ve gruplama | RAG filtreleme |
| `oncelik` | Toplama sırası | Hangi belgeler önce doldurulacak |
| `kaynaklar` | Birincil erişim | Metin yoksa kullanıcıya verilecek adres |
| `metin_durumu` | Dosyada gerçekten metin var mı | ⚠️ `iskelet` ise alıntı yasağı |
| `dogrulama` | Künye teyit edildi mi | ⚠️ `dogrulanmadi` ise kesinlik iddia edilmez |
| `son_guncelleme` | Bayatlama kontrolü | Sayısal değerlerde uyarı |

## Metin blok işareti

Resmî metin daima şu işaretler arasında bulunur ve **birebir** korunur:

```
<!-- METIN:BASLANGIC -->
…
<!-- METIN:BITIS -->
```

Bu blok dışındaki her şey derlemedir.

## Doğrulama kuralları (`scripts/dogrula.py`)

1. Zorunlu alanların tamamı var mı?
2. `id` dosya adıyla aynı mı, depoda benzersiz mi?
3. `tur`, `durum`, `metin_durumu`, `dogrulama.durum` enum değerlerinde mi?
4. `oncelik` ∈ {1,2,3} mü?
5. `kaynaklar` en az bir `https://` adres içeriyor mu?
6. Tarih alanları `YYYY-AA-GG` biçiminde mi?
7. `dogrulama.durum: dogrulandi` ise `tarih` ve `yontem` dolu mu?
8. `metin_durumu: tam-metin` ise `METIN:BASLANGIC` bloğu boş değil mi?
9. `brans` ve `etiketler` boş değil mi?
10. Kütükteki (`data/kaynaklar.yaml`) her kaydın dosyası var mı?
