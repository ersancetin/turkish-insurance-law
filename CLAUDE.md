# Claude / kod ajanı notu

Bu depodaki çalışma kuralları **`AGENTS.md`** dosyasındadır — önce onu okuyun.

Kısa özet:

- `data/kaynaklar.yaml` tek gerçek kaynaktır. Belge eklemek = buraya kayıt eklemek.
- `INDEX.md`, `data/kaynaklar.json`, `meta/durum-raporu.md` otomatik üretilir; elle düzenlemeyin.
- Değişiklikten sonra: `python3 scripts/uret.py && python3 scripts/dogrula.py`
- `metin_durumu: iskelet` olan dosyalarda resmî metin yoktur — alıntılamayın.
- Künyeler (`resmi_gazete`) **doğrulanmamıştır**; `dogrulama.durum` alanını kontrol edin.
