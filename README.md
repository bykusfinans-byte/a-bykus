# BIST AI Pro V2

BIST hisseleri için teknik + temel analiz yapan, AI Skoru üreten ve bu skora
göre **kendi kararını verip otomatik alım/satım yapan** sanal (gerçek para
kullanmayan) bir bot. Sonuçlar GitHub Actions ile periyodik olarak üretilir ve
GitHub Pages üzerinden şifre korumalı bir panelde gösterilir.

⚠️ **Bu bir simülasyondur.** Gerçek para kullanılmaz, yatırım tavsiyesi değildir.

## Mimari

```
GitHub Actions (cron, günde 3 kez)
        │
        ▼
   src/main.py  →  tüm hisseleri tarar (yfinance)
        │              → AI Skoru üretir
        │              → bot kurallarına göre otomatik AL/SAT yapar
        ▼
docs/data/sonuc.json    (tarama sonuçları)
docs/data/portfoy.json  (bot portföyü + işlem geçmişi)
        │
        ▼
   docs/index.html  (GitHub Pages - statik sayfa, JSON'ları okuyup gösterir)
```

GitHub Pages sadece statik dosya sunabildiği için Python kodu tarayıcıda
**değil**, GitHub Actions'ın sunucularında, zamanlanmış olarak çalışır. Sen
siteyi her açtığında en son çalışan taramanın sonucunu görürsün.

## Kurulum

1. Bu klasörü GitHub'daki boş reponun içine yükle (repo kök dizinine).
2. Repo → **Settings → Pages** → "Build and deployment" → Source: **Deploy
   from a branch** → Branch: `main`, klasör: **/docs** → Save.
3. Repo → **Settings → Actions → General** → "Workflow permissions" →
   **Read and write permissions** seçeneğini işaretle ve kaydet (Actions'ın
   sonuçları commit edebilmesi için gerekli).
4. Repo → **Actions** sekmesi → "BIST AI Pro Tarama" workflow'unu seç → **Run
   workflow** ile ilk taramayı elle tetikle (cron saatini beklemeden test
   etmek için).
5. Birkaç dakika sonra `https://KULLANICI_ADIN.github.io/REPO_ADIN/`
   adresinde sonucu göreceksin.

## Şifreyi değiştirme

`docs/app.js` içindeki `SIFRE_HASH` değeri, şifrenin SHA-256 hash'idir.
Varsayılan şifre **1234**'tür — ilk iş bunu değiştir:

1. Tarayıcı konsolunu aç (F12), şunu çalıştır:
   ```js
   await crypto.subtle.digest("SHA-256", new TextEncoder().encode("YENİ_ŞİFREN"))
     .then(b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2,"0")).join(""))
   ```
2. Çıkan metni `docs/app.js` içindeki `SIFRE_HASH` satırına yapıştır, commit'le.

**Not:** Bu koruma sadece rastgele ziyaretçileri uzak tutar; GitHub Pages'teki
hiçbir dosya gerçekten gizli değildir (herkes `docs/data/sonuc.json`'u
doğrudan da açabilir). Gerçek gizlilik istersen GitHub'ın ücretli planındaki
private repo + Pages özelliğini kullanman gerekir.

## "Yeni Tarama Başlat" butonu (siteden GitHub Actions tetikleme)

Site üzerindeki **▶ Yeni Tarama Başlat** butonu, GitHub Actions'ı anlık olarak
tetikler (cron saatini beklemeden). Bunun çalışması için `docs/app.js`
dosyasının başındaki üç değeri doldurman gerekiyor:

```js
const GITHUB_OWNER = "kullanici-adin";
const GITHUB_REPO = "repo-adin";
const GITHUB_TOKEN = "...";
```

**Token'ı şöyle oluştur (fine-grained personal access token):**

1. GitHub → sağ üst profil fotoğrafın → **Settings**
2. Sol menüde en altta **Developer settings**
3. **Personal access tokens → Fine-grained tokens → Generate new token**
4. **Repository access** → "Only select repositories" → bu repoyu seç
5. **Permissions → Repository permissions** → **Actions** satırını bul,
   **Read and write** seç. **Başka hiçbir izin verme** (Contents dahil —
   koda yazma yetkisi vermene gerek yok, sadece Actions'ı tetikleyecek).
6. Süre (expiration) belirle, oluştur, çıkan token'ı kopyala (bir daha
   gösterilmez).
7. Token'ı `docs/app.js`'e yapıştır, commit'le.

⚠️ **Bu token, sitendeki herkes tarafından görülebilir** (tarayıcı "Kaynağı
görüntüle" / Ağ sekmesinden). Bu yüzden **sadece** "Actions: Read and write"
yetkisi ver — başka bir izin verirsen (özellikle "Contents: write") biri bu
token'ı alıp reponun koduna yazabilir. Actions-only bir token ile en kötü
ihtimalle biri taramanı gereksiz yere spam gibi tetikleyip GitHub Actions
dakikalarını tüketebilir (ücretsiz planda ayda 2000 dakika) — koduna veya
verine zarar veremez.

Token'ı doldurmadan butona basarsan site seni uyarır, hiçbir şey göndermez.


## Bot kurallarını değiştirme

`src/settings.py` içindeki bu değerleri değiştirerek botun davranışını
ayarlayabilirsin:

| Ayar | Anlamı | Varsayılan |
|---|---|---|
| `BOT_BASLANGIC_SERMAYE` | Sanal başlangıç sermayesi | 100.000 ₺ |
| `BOT_MAX_POZISYON` | Aynı anda taşınacak maksimum hisse sayısı | 8 |
| `BOT_ALIM_ESIGI` | Bu AI Skorunun üstündeki hisseler otomatik alınır | 70 |
| `BOT_SATIM_ESIGI` | Skor bu değerin altına düşerse pozisyon kapatılır | 50 |

Stop-loss ve hedef fiyata değme kuralı skor eşiğinden bağımsız her zaman
çalışır (`risk_motoru.py` → ATR bazlı hesaplanır).

## Hisse listesini genişletme

`src/hisseler.py` içindeki `BIST_HISSELERI` listesine istediğin kadar BIST
kodu ekleyebilirsin (`.IS` uzantısını yazma). Liste ne kadar uzarsa tarama o
kadar sürer — `Settings.SLEEP` (varsayılan 0.3 sn) her hisse arası bekleme
süresidir, Yahoo Finance'ın seni engellememesi için var.

## Taramanın zamanlaması

`.github/workflows/tarama.yml` içindeki `cron` satırlarını değiştirerek
sıklığı ayarlayabilirsin. Şu an hafta içi TR saatiyle 09:30, 13:30 ve 18:00'de
çalışacak şekilde ayarlı (cron UTC kullanır, TR = UTC+3).

## Yerelde test etme

```bash
pip install -r requirements.txt
cd src
python main.py
```

Bu, `docs/data/sonuc.json` ve `docs/data/portfoy.json` dosyalarını üretir;
`docs/index.html`'i tarayıcıda açarak (ya da `python -m http.server` ile
`docs` klasöründen sunarak) sonucu yerelde görebilirsin.

## Bilinen sınırlamalar

- Yahoo Finance verisi gecikmeli/tutarsız olabilir; `yfinance` resmi bir API
  değildir, ileride kırılabilir.
- Tüm liste taranırken her hisse için 2 ayrı ağ isteği yapılır (fiyat verisi +
  temel veri); büyük listelerde GitHub Actions'ın 6 saatlik iş süresi limitine
  yaklaşmamaya dikkat et.
- Bot kararları geriye dönük test edilmemiştir (backtest yok); üretimdeki
  davranışı bir süre gözlemlemeden gerçek sermaye kararlarına temel alma.
