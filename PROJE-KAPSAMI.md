# Proje Kapsamı

**Sürüm:** 0.1.0 · **Tarih:** 2026-08-19 · **Durum:** Faz 1 tamamlandı

---

## 1. Amaç

Türk sigorta hukukunun **birincil kaynaklarını** (mevzuat + düzenleyici işlem +
içtihat) tek bir depoda, tutarlı künyeli Markdown dosyaları hâlinde toplamak;
hem insanın hem de yapay zekâ ajanlarının **atıf yapılabilir, izlenebilir ve
güncel** biçimde kullanabileceği bir kaynak katmanı kurmak.

## 2. Kapsam içi (IN SCOPE)

| # | Kategori | Örnek |
| --- | --- | --- |
| 1 | Kanunlar | 5684 Sigortacılık K., 6102 TTK m.1401-1520, 2918 KTK m.85-115, 4632 BES K., 6305 Afet Sigortaları K., 5363 Tarım Sigortaları K., 6098 TBK ilgili hükümler, 5510 rücu hükümleri |
| 2 | Cumhurbaşkanlığı kararnameleri | 47 s. CBK (SEDDK teşkilatı) |
| 3 | Yönetmelikler | Acente, eksper, broker, bilgilendirme, teknik karşılıklar, mali bünye, destek hizmetleri, özel sağlık, hayat grubu, tahkim, SBM, katılım sigortacılığı, BES, DASK, TARSİM |
| 4 | Tebliğ / tarife / talimat | DASK tarife ve talimatı, ZMSS azami prim tarifesi, hesap planı |
| 5 | **Genel şartlar** | ZMSS (trafik), kasko, İMM, yangın, zorunlu deprem, sağlık, hayat, ferdi kaza, nakliyat, mühendislik, tarım, kredi, kefalet, hukuksal koruma, tüm zorunlu sorumluluk branşları |
| 6 | Genel şart ekleri ve klozlar | Sürekli sakatlık / destekten yoksun kalma / değer kaybı hesap ekleri, GLKHHKNH, terör, deprem klozları |
| 7 | **SEDDK genelgeleri** | Sigortacılık, BES ve katılım sigortacılığı genelgelerinin tam serisi |
| 8 | **Sektör ve mevzuat duyuruları** | SEDDK duyuru arşivinin tamamı |
| 9 | **SEDDK bildirgeleri / ilke kararları / rehberleri** | Uygulama rehberleri, denetim rehberleri |
| 10 | **Sigorta Tahkim Komisyonu** | Tahkim yönetmeliği, duyurular, parasal sınırlar, başvuru ücret tarifesi, hakem listeleri, ilkesel kararlar |
| 11 | İçtihat | AYM norm denetimi kararları, Yargıtay yerleşik içtihadı, Danıştay iptal kararları, BAM kararları |
| 12 | Kurum dosyaları | SBM, DASK, TARSİM, Güvence Hesabı, TSB, SEGEM, TOBB icra komiteleri, EGM |
| 13 | Derleme rehberler | Kavram sözlüğü, süreç akışları, tazminat hesaplama notları, karşılaştırma tabloları |

## 3. Kapsam dışı (OUT OF SCOPE)

- Sigorta şirketlerinin **özel şartları** ve ürün poliçe metinleri (marka bazlı, telif riskli).
- Ticari veri tabanlarından (Lexpera, Kazancı, Legalbank vb.) **kopyalanan içerik**.
- Vergi, muhasebe ve aktüerya hesap tabloları — yalnızca mevzuat düzeyinde atıf yapılır.
- Hukuki tavsiye niteliğinde yorum; depo **kaynak sunar, mütalaa vermez**.
- Kişisel veri içeren hasar dosyaları, gerçek kişi taraflı karar metinlerinin anonimleştirilmemiş hâli.

## 4. Kalite ve kabul kriterleri

Bir belge "tamamlandı" sayılabilmesi için:

1. `metin_durumu: tam-metin` — resmî metnin tamamı `<!-- METIN:BASLANGIC -->` bloğunda.
2. `dogrulama.durum: dogrulandi` — künye (RG tarih/sayı) resmî kaynaktan teyit edilmiş.
3. `kaynaklar:` en az bir **birincil** (resmigazete.gov.tr / mevzuat.gov.tr / seddk.gov.tr) adres.
4. Madde başlıkları `## Madde N — Başlık` düzeninde.
5. Değişiklik geçmişi tablosu doldurulmuş; iptal edilen hükümler `> [!CAUTION]` ile işaretli.
6. `python3 scripts/dogrula.py` hatasız geçiyor.

## 5. Yol haritası

### Faz 1 — İskelet (✅ tamamlandı)
- Kapsam tanımı, klasör mimarisi, taksonomi, künye şeması.
- 117 kayıtlık kaynak kütüğü (`data/kaynaklar.yaml`).
- Tüm kayıtlar için künyeli `.md` iskeleti, `INDEX.md`, durum raporu.
- Üretici / doğrulayıcı / toplayıcı betikleri.

### Faz 2 — Birincil metinlerin toplanması (⛔ ağ erişimi gerekiyor)
- P1 kayıtlar: 5684, 6102, 2918, ZMSS genel şartları, kasko, sağlık, hayat, tahkim mevzuatı.
- `scripts/cek.py` ile HTML/PDF → Markdown dönüşümü, künye doğrulaması.
- Gerekli alan adı izinleri: `seddk.gov.tr`, `mevzuat.gov.tr`, `resmigazete.gov.tr`,
  `tsb.org.tr`, `sigortatahkim.org`, `dask.gov.tr`, `tarsim.gov.tr`,
  `guvencehesabi.org.tr`, `normkararlarbilgibankasi.anayasa.gov.tr`,
  `karararama.yargitay.gov.tr`, `karararama.danistay.gov.tr`.

### Faz 3 — Seri toplama
- SEDDK genelge / sektör duyurusu / mevzuat duyurusu arşivlerinin taranıp
  her kaydın ayrı `.md` olarak açılması (`tur: koleksiyon` kayıtları genişletilir).
- Sigorta Tahkim Komisyonu duyuru arşivi.

### Faz 4 — İçtihat katmanı
- AYM iptal kararlarının tam metni ve mevzuata etkisinin belgelerde çapraz bağlanması.
- Yargıtay yerleşik içtihadının konu bazlı derlenmesi.

### Faz 5 — Otomasyon ve süreklilik
- Haftalık Resmî Gazete taraması; değişiklikleri kütüğe düşüren iş akışı.
- Değişiklik geçmişi tablolarının otomatik güncellenmesi.
- Yapay zekâ ajanları için gömme (embedding) çıktısı / arama uçları.

## 6. Riskler ve sınırlar

| Risk | Etki | Azaltım |
| --- | --- | --- |
| Ağ erişiminin kısıtlı olması | Tam metinler eklenemiyor | İskelet + kaynak adresi üretildi; alan adı izni talep edilecek |
| Künye bilgilerinin doğrulanmamış olması | Yanlış atıf | Her belgede `dogrulama.durum: dogrulanmadi` uyarısı zorunlu |
| Mevzuatın hızlı değişmesi | Metnin bayatlaması | `son_guncelleme` alanı + Faz 5 otomasyonu |
| Genel şart eklerinin iptal edilmiş olması | Hatalı hesaplama | İptal kararları ayrı belge; ilgili genel şartta çapraz uyarı |
| Telifli derlemelerden kopyalama | Hukuki risk | Yalnızca birincil resmî kaynak; ticari veri tabanı içeriği alınmaz |

## 7. Başarı ölçütü

- P1 kayıtların **%100'ü** tam metin + doğrulanmış künye.
- `scripts/dogrula.py` CI'da hatasız.
- Bir yapay zekâ ajanının `AGENTS.md` + `INDEX.md` okuyarak, ek talimata gerek
  kalmadan doğru belgeyi bulup atıf yapabilmesi.
