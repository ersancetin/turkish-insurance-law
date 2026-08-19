# Taksonomi — Belge Türleri, Branşlar ve Etiketler

## 1. Belge türleri (`tur`)

| Değer | Anlamı | Hiyerarşideki yeri |
| --- | --- | --- |
| `kanun` | TBMM kanunu | En üst (Anayasa altı) |
| `cbk` | Cumhurbaşkanlığı kararnamesi | Kanun düzeyi (CBK alanı) |
| `yonetmelik` | Kurum/Bakanlık yönetmeliği | Kanun altı |
| `teblig` | Tebliğ | Yönetmelik altı |
| `tarife` | Tarife, talimat, ücret cetveli | Yönetmelik altı, dönemsel |
| `genel-sart` | Sigorta genel şartları | Düzenleyici işlem; sözleşme içeriğini belirler |
| `genelge` | SEDDK genelgesi | Uygulama talimatı |
| `sektor-duyurusu` | Sektöre yönelik duyuru | Bağlayıcılığı sınırlı, uygulama yönlendirir |
| `bildirge` | Bildirge / ilke kararı | Kurum politikası |
| `rehber` | Uygulama veya denetim rehberi | Yol gösterici |
| `karar` | Yargı kararı (AYM, Yargıtay, Danıştay, BAM) | Normu yorumlar / iptal eder |
| `kurum` | Kurum dosyası (SBM, DASK …) | Bilgi/derleme |
| `koleksiyon` | Tek belge değil, toplanacak seri | Görev kaydı |
| `rapor` | Faaliyet raporu, istatistik | Bilgi |

## 2. Branşlar (`brans`)

| Değer | Kapsam |
| --- | --- |
| `genel` | Branş üstü / tüm sigortacılık |
| `sorumluluk` | Zorunlu ve ihtiyari mali sorumluluk |
| `motorlu-arac` | Trafik/ZMSS, İMM ile ilgili |
| `kara-araclari` | Kasko |
| `yangin` | Yangın ve bağlı teminatlar |
| `dogal-afet` | Zorunlu deprem, DASK |
| `nakliyat` | Emtia, tekne, yat, kıymet |
| `muhendislik` | İnşaat, montaj, makine kırılması, elektronik cihaz |
| `saglik` | Özel sağlık, seyahat sağlık, yabancı sağlık |
| `hayat` | Hayat, kredi hayat |
| `ferdi-kaza` | Ferdi kaza, koltuk ferdi kaza |
| `tarim` | Devlet destekli tarım sigortaları, TARSİM |
| `kredi` | Kredi ve alacak sigortası |
| `kefalet` | Kefalet sigortası |
| `hukuksal-koruma` | Hukuksal koruma |
| `mesleki` | Mesleki sorumluluk, malpraktis |
| `tasimacilik` | Karayolu/deniz taşımacılık sorumluluğu |
| `deniz` | Deniz araçları, kıyı tesisleri |
| `bes` | Bireysel emeklilik |
| `katilim` | Katılım sigortacılığı (tekafül) |
| `aracilar` | Acente, eksper, broker |
| `hasar` | Hasar süreçleri, destek hizmetleri |
| `uyusmazlik` | Tahkim, dava, alternatif çözüm |
| `veri` | SBM, veri paylaşımı, KVKK kesişimi |

## 3. Yürürlük durumu (`durum`)

| Değer | Anlamı | Ajan davranışı |
| --- | --- | --- |
| `yururlukte` | Geçerli | Normal kullanım |
| `kismen-iptal` | Bazı hükümleri iptal edilmiş | İptal kararını da oku, uyarı ver |
| `degisiklik-bekliyor` | Yakın tarihli değişiklik içeriyor / yürürlük tarihi ileri | `son_guncelleme` uyarısı ver |
| `mulga` | Yürürlükten kaldırılmış | Yalnızca tarihsel atıf |
| `bilinmiyor` | Teyit edilmemiş | Kullanıcıyı uyar |

## 4. Öncelik (`oncelik`)

| Değer | Anlamı | Örnek |
| --- | --- | --- |
| `1` | Kritik — günlük uygulamada sürekli kullanılır | 5684, TTK sigorta hükümleri, ZMSS genel şartları, kasko, tahkim mevzuatı |
| `2` | Önemli — sık başvurulur | Acente yönetmeliği, işveren sorumluluk, kefalet |
| `3` | Tamamlayıcı — dar alanda kullanılır | Tüpgaz, arıcılık sigortası, EGM dosyası |

## 5. Sık kullanılan etiketler (`etiketler`)

**Trafik/ZMSS:** `zmss` `trafik` `isleten-sorumlulugu` `dogrudan-dava`
`destekten-yoksun-kalma` `surekli-sakatlik` `deger-kaybi` `teminat-disi-haller`
`hatir-tasimasi` `rucu` `guvence-hesabi` `basamak` `hasarsizlik-indirimi`
`riskli-sigortalilar-havuzu` `trh-2010` `teknik-faiz`

**Sözleşme hukuku:** `beyan-yukumlulugu` `rizikonun-ihbari` `prim-odenmemesi`
`halefiyet` `zamanasimi` `lehtar` `eksik-sigorta` `asiri-sigorta` `muafiyet`

**Sağlık/hayat:** `omur-boyu-yenileme-garantisi` `bekleme-suresi`
`onceden-var-olan-hastalik` `gecis-islemleri` `tamamlayici-saglik` `istira` `ikraz`

**Aracılar:** `acente` `eksper` `broker` `levha-kaydi` `teknik-personel` `segem`

**Tahkim:** `tahkim` `hakem` `itiraz-hakem-heyeti` `parasal-sinir` `basvuru-ucreti`
`ilkesel-karar`

**Kurumsal/denetim:** `sermaye-yeterliligi` `teknik-karsilik` `muallak-hasar-karsiligi`
`ic-kontrol` `bagimsiz-denetim` `masak` `kvkk`

**Süreç:** `seri-toplama` `arsiv` `yillik-guncelleme`

## 6. Etiket ekleme kuralı

- Küçük harf, kebab-case, Türkçe karakter yok (`değer-kaybı` ❌ → `deger-kaybi` ✅).
- Yeni etiket eklerken bu dosyaya da işleyin.
- Etiketler **arama içindir**; hukuki nitelendirme yapmaz.
