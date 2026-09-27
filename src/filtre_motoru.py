# ==========================================================
# BIST AI PRO V2
# MODÜL 16 - FİLTRE MOTORU (Teknik Dizilim Süzgeci)
#
# Kural: Fiyat > EMA9 > EMA21 > SMA50 > SMA200
#        VE  MACD > 0
#        VE  ADX > Settings.FILTRE_ADX_ESIK
#        VE  Settings.FILTRE_RSI_ALT <= RSI <= Settings.FILTRE_RSI_UST
# ==========================================================

from settings import Settings


class FiltreMotoru:

    def __init__(self, df):
        self.son = df.iloc[-1]

    # ------------------------------------------------------

    def hesapla(self):

        son = self.son

        fiyat = son["Close"]
        ema9 = son["EMA9"]
        ema21 = son["EMA21"]
        sma50 = son["SMA50"]
        sma200 = son["SMA200"]
        adx = son["ADX"]
        macd = son["MACD"]
        rsi = son["RSI"]

        dizilim_uygun = fiyat > ema9 > ema21 > sma50 > sma200
        macd_pozitif = macd > 0
        adx_guclu = adx > Settings.FILTRE_ADX_ESIK
        rsi_normal = Settings.FILTRE_RSI_ALT <= rsi <= Settings.FILTRE_RSI_UST

        gecti = dizilim_uygun and macd_pozitif and adx_guclu and rsi_normal

        return {
            "Fiyat": round(fiyat, 2),
            "EMA9": round(ema9, 2),
            "EMA21": round(ema21, 2),
            "SMA50": round(sma50, 2),
            "SMA200": round(sma200, 2),
            "ADX": round(adx, 2),
            "MACD": round(macd, 2),
            "RSI": round(rsi, 2),
            "Dizilim": dizilim_uygun,
            "Gecti": gecti,
        }
