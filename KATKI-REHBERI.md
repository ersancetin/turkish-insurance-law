# Katkı Rehberi

## Altın kural

**`.md` dosyalarını elle oluşturmayın.** Yeni belge = `data/kaynaklar.yaml` içine
yeni kayıt + `python3 scripts/uret.py`.

## 1. Yeni belge ekleme

```yaml
  - id: yon-ornek-yonetmelik            # kebab-case, benzersiz, dosya adı olur
    baslik: "Örnek Yönetmelik"          # resmî tam ad
    tur: yonetmelik                     # meta/taksonomi.md'deki türlerden biri
    klasor: belgeler/03-yonetmelikler/sigortacilik
    brans: [genel]
    otorite: SEDDK
    numara: null
    rg_tarihi: "2026-01-15"             # bilinmiyorsa null
    rg_sayisi: "33000"                  # bilinmiyorsa null
    durum: yururlukte
    oncelik: 2                          # 1 kritik, 2 önemli, 3 tamamlayıcı
    kaynaklar:
      - "https://www.resmigazete.gov.tr/..."
    etiketler: [ornek, etiket]
    ozet: "Tek cümlelik kapsam açıklaması."
```

Sonra:

```bash
python3 scripts/uret.py      # yeni iskeleti + INDEX + raporu üretir
python3 scripts/dogrula.py   # şema denetimi
```

## 2. Bir iskelete resmî metin ekleme

1. Belgeyi açın, künyedeki `kaynaklar` adresinden **resmî metni** alın.
2. `<!-- METIN:BASLANGIC -->` ve `<!-- METIN:BITIS -->` arasını doldurun.
3. Biçimlendirme kuralları:
   - Madde başlığı: `## Madde 5 — Teminat dışında kalan hâller`
   - Genel şartlarda bölüm: `## A.3 — Teminat Dışında Kalan Hâller`
   - Fıkralar madde işareti veya numaralı liste; **metni değiştirmeyin**.
   - Değişiklik dipnotu, ilgili maddenin hemen altında:
     `> Değişiklik: RG 04.12.2021/31679 ile değiştirilmiştir.`
   - İptal edilen hüküm:
     ```
     > [!CAUTION]
     > Bu hüküm AYM E.2021/82, K.2022/167 kararıyla iptal edilmiştir (RG 14.02.2023).
     ```
4. Frontmatter'ı güncelleyin:
   ```yaml
   metin_durumu: tam-metin      # iskelet → ozet → tam-metin
   dogrulama:
     durum: dogrulandi
     tarih: "2026-08-19"
     yontem: "resmigazete.gov.tr üzerinden karşılaştırıldı"
   son_guncelleme: "2026-08-19"
   ```
5. `## Değişiklik geçmişi` tablosunu doldurun.
6. `python3 scripts/dogrula.py`

## 3. Koleksiyon kayıtlarını genişletme

`tur: koleksiyon` kayıtları (SEDDK genelgeleri, sektör duyuruları, tahkim
duyuruları) tek bir belge değil, **bir seriyi** temsil eder. Seriyi tararken
bulduğunuz her belge için kütüğe ayrı kayıt açın:

```yaml
  - id: genelge-2025-28-ozel-saglik-uygulama
    baslik: "2025/28 sayılı Özel Sağlık Sigortaları Yönetmeliğinin Uygulama Esaslarına İlişkin Genelge"
    tur: genelge
    klasor: belgeler/06-genelgeler/sigortacilik
    numara: "2025/28"
    ...
```

Koleksiyon kaydını silmeyin; serinin izlenmesi için kalsın.

## 4. İsimlendirme kuralları

| Öğe | Kural | Örnek |
| --- | --- | --- |
| `id` | kebab-case, Türkçe karakter yok | `gs-zmss-trafik` |
| Kanun | `<numara>-<kısa-ad>` | `5684-sigortacilik-kanunu` |
| Yönetmelik | `yon-<kısa-ad>` | `yon-sigorta-acenteleri` |
| Genel şart | `gs-<branş-kısa-ad>` | `gs-kasko` |
| Genelge | `genelge-<yıl>-<no>-<konu>` | `genelge-2025-28-ozel-saglik-uygulama` |
| Duyuru | `duyuru-<yyyy-aa-gg>-<konu>` | `duyuru-2026-05-22-ozel-saglik-yeni-donem` |
| Karar | `<mahkeme>-<esas>-<karar>` | `aym-e2021-82-k2022-167` |
| Tebliğ/tarife | `teb-` / `tarife-` öneki | `teb-zorunlu-deprem-tarife-talimat` |

## 5. Kaynak politikası

**Kullanılacak (birincil):**
`resmigazete.gov.tr`, `mevzuat.gov.tr`, `seddk.gov.tr`, `sigortatahkim.org`,
`dask.gov.tr`, `tarsim.gov.tr`, `guvencehesabi.org.tr`,
`normkararlarbilgibankasi.anayasa.gov.tr`, `karararama.yargitay.gov.tr`,
`karararama.danistay.gov.tr`, `tsb.org.tr` (derleme, ikincil ama açık).

**Kullanılmayacak:** Lexpera, Kazancı, Legalbank ve benzeri **abonelik gerektiren
ticari veri tabanları** — bu kaynaklardan metin kopyalamak telif ihlalidir.
Bu sitelere yalnızca `## Notlar` bölümünde bibliyografik atıf yapılabilir.

## 6. Commit mesajı

```
<alan>: <kısa açıklama>

kutuk: 12 yeni genelge kaydı eklendi
metin: gs-kasko tam metin + künye doğrulaması
yapi: 09-tahkim altına ilkesel-kararlar klasörü
rehber: destekten yoksun kalma hesabı notu güncellendi
```

## 7. Denetim

```bash
python3 scripts/dogrula.py          # şema, id tekrarı, kırık iç bağlantı, künye tutarlılığı
python3 scripts/uret.py --kontrol   # kütükte olup dosyası olmayan kayıtlar
```
