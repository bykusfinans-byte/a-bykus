# ==========================================================
# BIST AI PRO V2
# AYARLAR
# ==========================================================


class Settings:

    # ---- Veri ----
    # NOT: Bu sistem GÜNLÜK değil, 4 SAATLİK mum bazlı çalışır.
    # yfinance'tan saatlik (1h) veri çekilip BIST seansına göre
    # (10:00-14:00 ve 14:00-18:00) 4 saatlik mumlara birleştirilir.
    # Bu yüzden EMA200 gibi göstergeler "200 gün" değil "200 tane
    # 4 saatlik mum" (~yaklaşık 100 işlem günü, ~5 ay) anlamına gelir.
    INTERVAL = "1h"
    PERIOD = "1y"       # yfinance'ın 1h veri için izin verdiği maksimum aralık 730 gün
    MIN_BAR = 220        # 220 adet 4 saatlik mum (~110 işlem günü)
    SLEEP = 0.3  # her hisse taraması arası bekleme (saniye) - rate-limit koruması

    # ---- Hareketli ortalamalar ----
    # NOT: Trend dizilimi artık EMA9 > EMA21 > EMA50 üzerinden hesaplanıyor
    # (4 saatlik sistemde EMA100/EMA200 çok geriden takip ettiği için kaldırıldı).
    # SMA50/SMA200 hâlâ "Teknik Dizilim Süzgeci" tablosunda uzun vade
    # referansı olarak kullanılıyor.
    EMA9 = 9
    EMA21 = 21
    EMA50 = 50
    SMA50 = 50
    SMA200 = 200

    # ---- Göstergeler ----
    RSI = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    ADX = 14
    ATR = 14
    BB = 20
    MFI = 14

    # ---- Risk / hedef çarpanları (ATR bazlı) ----
    ATR_STOP = 2
    ATR_TARGET1 = 2
    ATR_TARGET2 = 4
    ATR_TARGET3 = 6

    # ---- Teknik Skor ağırlıkları (TrendMotoru + MomentumMotoru + HacimMotoru) ----
    W_TREND = 0.40
    W_MOMENTUM = 0.35
    W_HACIM = 0.25

    # ---- AI Skor ağırlıkları (Teknik + Temel + Risk) ----
    W_TEKNIK = 0.50
    W_TEMEL = 0.30
    W_RISK = 0.20

    # ---- Bot (otomatik alım/satım) ayarları ----
    BOT_BASLANGIC_SERMAYE = 100_000
    BOT_MAX_POZISYON = 8          # aynı anda taşınabilecek maksimum hisse sayısı
    BOT_ALIM_ESIGI = 70           # AI Skoru >= bu değer ise ALIM adayı
    BOT_SATIM_ESIGI = 50          # AI Skoru < bu değer ise pozisyon kapatılır (sinyal bozuldu)
    # Not: Stop-Loss ve Hedef fiyatına değme kuralı skor eşiğinden bağımsız her zaman çalışır.

    # ---- Teknik dizilim süzgeci (site "Teknik Süzgeç" tablosu) ----
    # Fiyat > EMA9 > EMA21 > SMA50 > SMA200  VE  MACD > 0  VE  ADX > FILTRE_ADX_ESIK
    # VE  FILTRE_RSI_ALT <= RSI <= FILTRE_RSI_UST  ise hisse "güçlü dizilim" sayılır.
    FILTRE_ADX_ESIK = 25
    FILTRE_RSI_ALT = 20
    FILTRE_RSI_UST = 80
