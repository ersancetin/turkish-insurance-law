# Yapay Zekâ Ajanları İçin Kullanım Sözleşmesi

Bu depo, yapay zekâ ajanlarının (LLM, RAG sistemleri, kod ajanları) **doğrudan
tüketmesi** için tasarlanmıştır. Aşağıdaki kurallara uyun.

---

## 1. Nereden başlanır

| İhtiyaç | Okunacak dosya |
| --- | --- |
| Depoda ne var? | `INDEX.md` (otomatik üretilir, 117 kayıt) |
| Makine okunur kütük | `data/kaynaklar.json` |
| Kavram/etiket sözlüğü | `meta/taksonomi.md` |
| Künye alanlarının anlamı | `meta/frontmatter-semasi.md` |
| Kapsam ve sınırlar | `PROJE-KAPSAMI.md` |
| Ne kadarı tamamlandı | `meta/durum-raporu.md` |

**Tam metin arıyorsanız** doğrudan `data/kaynaklar.json` içinde `etiketler`,
`brans` ve `baslik` alanlarında arayın; eşleşen kaydın `klasor` + `id` alanları
dosya yolunu verir: `{klasor}/{id}.md`.

## 2. Belge okuma protokolü

Her belge iki katmandan oluşur:

```
--- YAML frontmatter (künye) ---
id, baslik, tur, otorite, numara, resmi_gazete{tarih,sayi},
durum, brans[], etiketler[], oncelik, kaynaklar[],
metin_durumu, dogrulama{durum,tarih,yontem}, son_guncelleme
---
Markdown gövde: Künye tablosu → Özet → Resmî metin → Değişiklik geçmişi
                → İlgili belgeler → Kaynaklar → Notlar
```

Resmî metin daima şu işaretler arasındadır:

```
<!-- METIN:BASLANGIC -->
… resmî metin …
<!-- METIN:BITIS -->
```

Alıntı yaparken **yalnızca bu blok** birincil metindir. Blok dışındaki her şey
(özet, not, etiket) **derleme yorumudur** ve resmî metin olarak sunulamaz.

## 3. Zorunlu güven kuralları

> [!CAUTION]
> **`metin_durumu: iskelet` olan bir dosyadan hukuki metin alıntılamayın.**
> Bu dosyalarda resmî metin yoktur; yalnızca künye ve özet vardır.

1. `dogrulama.durum: dogrulanmadi` ise, Resmî Gazete tarih/sayı bilgisini
   **kesin gerçek olarak sunmayın**; "doğrulanmamış künye" olarak nitelendirin.
2. `durum: kismen-iptal` ise, iptal kararını (`belgeler/10-ictihat/`) okumadan
   maddenin yürürlükte olduğunu **varsaymayın**.
3. `durum: degisiklik-bekliyor` ise, `son_guncelleme` tarihinden sonraki
   değişiklikleri kullanıcıya hatırlatın.
4. Metin bulamadığınızda **uydurmayın**. Doğru cevap: "bu belgenin tam metni
   depoda henüz yok, resmî kaynak: `<kaynaklar[0]>`".
5. Tazminat hesabı, prim, parasal sınır gibi **sayısal** bilgiler yıllık değişir;
   `son_guncelleme` tarihini mutlaka birlikte belirtin.

## 4. Atıf biçimi

Ajanlar üretilen metinde şu biçimi kullanmalıdır:

```
[Belge adı], [otorite], RG [tarih]/[sayı], m. [madde]
— kaynak: belgeler/<klasor>/<id>.md (künye doğrulama: dogrulandi|dogrulanmadi)
```

Örnek:

```
Karayolları Motorlu Araçlar Zorunlu Mali Sorumluluk Sigortası Genel Şartları,
SEDDK, RG 14.05.2015/29355, A.5 — kaynak:
belgeler/05-genel-sartlar/sorumluluk/gs-zmss-trafik.md (künye doğrulama: dogrulanmadi)
```

## 5. Depoya yazan ajanlar için

- **`.md` dosyalarını elle oluşturmayın.** Önce `data/kaynaklar.yaml` içine kayıt
  ekleyin, sonra `python3 scripts/uret.py` çalıştırın.
- `INDEX.md`, `data/kaynaklar.json`, `meta/durum-raporu.md` **otomatik üretilir** —
  elle düzenlemeyin, üzerine yazılır.
- Mevcut bir belgeye tam metin eklerken:
  1. `<!-- METIN:BASLANGIC -->` / `<!-- METIN:BITIS -->` arasını doldurun,
  2. frontmatter'da `metin_durumu: tam-metin` yapın,
  3. künyeyi teyit ettiyseniz `dogrulama.durum: dogrulandi` + `tarih` + `yontem` girin,
  4. `python3 scripts/dogrula.py` çalıştırın.
- Metni **kısaltmayın, özetlemeyin, modernize etmeyin**. Resmî metin blokta
  birebir durur; yorum `## Notlar` bölümüne yazılır.
- Ticari veri tabanlarından (Lexpera, Kazancı, Legalbank …) metin kopyalamayın;
  yalnızca birincil resmî kaynak kullanın.

## 6. Bilinen sınır: ağ erişimi

Depo, dış ağ erişimi engelli bir ortamda kuruldu. Kaynak alan adları
(`seddk.gov.tr`, `mevzuat.gov.tr`, `resmigazete.gov.tr`, `tsb.org.tr`,
`sigortatahkim.org` …) egress politikası tarafından bloke edildiğinden tam
metinler çekilemedi. Ağ erişimi olan bir ortamda:

```bash
python3 scripts/cek.py --oncelik 1      # P1 kayıtların kaynaklarını indir
```
