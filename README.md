# Türk Sigorta Hukuku — Kaynak Deposu

Türk sigorta hukukuna ilişkin **kanun, Cumhurbaşkanlığı kararnamesi, yönetmelik, tebliğ,
tarife, genel şart, genelge, sektör duyurusu, SEDDK bildirgesi, tahkim duyurusu ve
içtihat** metinlerini tek bir yerde, **Markdown** formatında, **yapay zekâ ajanlarının
doğrudan okuyabileceği** yapıda toplayan açık depo.

---

## Bu depo ne işe yarar?

| Kullanıcı | Kazanım |
| --- | --- |
| Avukat / hukuk bürosu | Dilekçe ve mütalaada tek tıkla doğru mevzuat metni ve künyesi |
| Yapay zekâ ajanı / RAG sistemi | Temiz Markdown + YAML künye = güvenilir bağlam (context) |
| Sigorta şirketi uyum birimi | Genelge/duyuru arşivinin izlenebilir hâli |
| Akademisyen | Değişiklik geçmişi ve iptal kararlarıyla birlikte konsolide kaynak |

## Depo yapısı

```
.
├── README.md                 Bu dosya
├── PROJE-KAPSAMI.md          Kapsam, sınırlar, yol haritası, kabul kriterleri
├── AGENTS.md                 Yapay zekâ ajanları için kullanım sözleşmesi
├── KATKI-REHBERI.md          Belge ekleme/doldurma kuralları
├── INDEX.md                  ⚙️ Otomatik üretilen ana dizin (117 kayıt)
│
├── data/
│   ├── kaynaklar.yaml        ⭐ TEK GERÇEK KAYNAK — tüm kütük burada
│   └── kaynaklar.json        ⚙️ Makine okunur türev (otomatik)
│
├── meta/
│   ├── taksonomi.md          Branş, belge türü ve etiket sözlüğü
│   ├── frontmatter-semasi.md YAML künye şeması ve alan tanımları
│   ├── belge-sablonu.md      Elle belge eklerken kullanılacak şablon
│   ├── durum-raporu.md       ⚙️ Kapsam/ilerleme raporu (otomatik)
│   └── parametreler.md       Yıl bazlı: teminat limitleri, tahkim parasal sınırları, faiz oranları
│
├── belgeler/
│   ├── 01-kanunlar/                      5684, 6102 TTK, 2918 KTK, 4632, 6305, 5363 …
│   ├── 02-cumhurbaskanligi-kararnameleri/ 47 s. CBK (SEDDK) …
│   ├── 03-yonetmelikler/
│   │   ├── sigortacilik/                 acente, eksper, broker, bilgilendirme …
│   │   ├── zorunlu-sigortalar/           ZMSS tarife uygulama esasları …
│   │   ├── bireysel-emeklilik/           BES, otomatik katılım, emeklilik fonları
│   │   ├── katilim-sigortaciligi/        tekafül
│   │   ├── afet-ve-tarim/                DASK, TARSİM
│   │   └── denetim-ve-mali-yapi/         teknik karşılıklar, sermaye yeterliliği …
│   ├── 04-tebligler-ve-tarifeler/        DASK tarifesi, ZMSS azami prim …
│   ├── 05-genel-sartlar/
│   │   ├── sorumluluk/                   ZMSS, İMM, malpraktis, mesleki, işveren …
│   │   ├── kara-araclari/                kasko
│   │   ├── yangin-ve-dogal-afet/         yangın, zorunlu deprem, hırsızlık, cam …
│   │   ├── nakliyat/ muhendislik/ tarim/ saglik-hayat-ferdi-kaza/
│   │   ├── kredi-kefalet-hukuksal-koruma/
│   │   └── klozlar-ve-ekler/             hesaplama tabloları, GLKHHKNH, terör klozu
│   ├── 06-genelgeler/                    SEDDK genelgeleri (sigortacılık / BES / katılım)
│   ├── 07-sektor-duyurulari/             sektör ve mevzuat duyuruları
│   ├── 08-seddk-kurumsal/                bildirgeler, ilke kararları, rehberler, raporlar
│   ├── 09-tahkim/                        Sigorta Tahkim Komisyonu: mevzuat, duyurular,
│   │                                     parasal sınırlar, ilkesel kararlar
│   ├── 10-ictihat/                       AYM, Yargıtay, Danıştay, BAM
│   └── 11-kurumlar/                      SBM, DASK, TARSİM, Güvence Hesabı, TSB, SEGEM,
│                                         TOBB, EGM
│
├── rehberler/                Derleme rehberler (kavram, süreç, hesaplama, karşılaştırma)
└── scripts/                  uret.py (üretici), dogrula.py (denetleyici), cek.py (toplayıcı)
```

## Hızlı başlangıç

```bash
pip install pyyaml                  # tek bağımlılık
python3 scripts/uret.py             # eksik belge iskeletlerini, INDEX ve raporu üret
python3 scripts/dogrula.py          # künye/şema tutarlılığını denetle
python3 scripts/cek.py --liste      # toplanacak kaynak adreslerini listele
```

## Mevcut durum (dürüst özet)

| Aşama | Durum |
| --- | --- |
| Kapsam belirleme | ✅ tamam |
| Klasör mimarisi | ✅ tamam |
| Kaynak kütüğü (117 kayıt) | ✅ tamam |
| Belge iskeletleri + künyeler | ✅ tamam |
| **Resmî tam metinlerin çekilmesi** | ⛔ **bekliyor** — bkz. aşağıdaki not |
| Künye doğrulama (RG tarih/sayı) | ⛔ bekliyor |

> [!IMPORTANT]
> **Metinler neden henüz yok?** Bu depo, dış ağ erişimi kısıtlı bir ortamda kuruldu:
> `seddk.gov.tr`, `mevzuat.gov.tr`, `resmigazete.gov.tr`, `tsb.org.tr`,
> `sigortatahkim.org` gibi kaynak alan adları egress politikası tarafından
> engellendi. Bu nedenle **iskelet + künye + kaynak adresi** üretildi;
> tam metinler `scripts/cek.py` ile ağ erişimi olan bir ortamda çekilmelidir.
> Kütükteki Resmî Gazete tarih/sayı bilgileri **doğrulanmamıştır**.

## Uyarı

Bu depo bir **derleme**dir, resmî yayın organı değildir. Hukuki sonuç doğuran her
işlemde **Resmî Gazete ve SEDDK'nın yayımladığı asıl metin** esastır. Her belgenin
künyesindeki `dogrulama.durum` alanı `dogrulandi` değilse, metin teyit edilmemiştir.

## Lisans

- Resmî mevzuat metinleri: 5846 sayılı FSEK m.31 uyarınca serbesttir.
- Bu depodaki derleme, özet, etiketleme ve rehber içerikleri: **CC BY 4.0**.
