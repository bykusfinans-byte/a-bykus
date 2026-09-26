# ==========================================================
# BIST AI PRO V2
# AYARLAR
# ==========================================================


class Settings:

    # ---- Veri ----
    PERIOD = "2y"
    MIN_BAR = 220
    SLEEP = 0.3  # her hisse taraması arası bekleme (saniye) - rate-limit koruması

    # ---- Hareketli ortalamalar ----
    EMA20 = 20
    EMA50 = 50
    EMA100 = 100
    EMA200 = 200

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
