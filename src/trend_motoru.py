# ==========================================================
# BIST AI PRO V2
# MODÜL 04 - TREND MOTORU
# ==========================================================


class TrendMotoru:

    def __init__(self, df):
        self.df = df
        self.son = df.iloc[-1]

    # ------------------------------------------------------

    def hesapla(self):

        puan = 0
        nedenler = []

        ema20 = self.son["EMA20"]
        ema50 = self.son["EMA50"]
        ema100 = self.son["EMA100"]
        ema200 = self.son["EMA200"]

        adx = self.son["ADX"]
        di_plus = self.son["DI_PLUS"]
        di_minus = self.son["DI_MINUS"]

        fiyat = self.son["Close"]

        # EMA dizilimi
        if ema20 > ema50:
            puan += 15
            nedenler.append("EMA20 > EMA50")

        if ema50 > ema100:
            puan += 15
            nedenler.append("EMA50 > EMA100")

        if ema100 > ema200:
            puan += 15
            nedenler.append("EMA100 > EMA200")

        # Fiyat EMA üzerinde mi?
        if fiyat > ema20:
            puan += 10
            nedenler.append("Fiyat EMA20 üzerinde")

        if fiyat > ema50:
            puan += 10
            nedenler.append("Fiyat EMA50 üzerinde")

        # ADX
        if adx >= 25:
            puan += 15
            nedenler.append("ADX güçlü")
        elif adx >= 20:
            puan += 10
            nedenler.append("ADX orta")
        elif adx >= 15:
            puan += 5
            nedenler.append("ADX zayıf")

        # DI
        if di_plus > di_minus:
            puan += 10
            nedenler.append("DI+ > DI-")

        # 20 günlük getiri
        getiri20 = (self.df["Close"].iloc[-1] / self.df["Close"].iloc[-20] - 1) * 100
        if getiri20 > 0:
            puan += 5
            nedenler.append("20 günlük yükseliş")

        # 50 günlük getiri
        getiri50 = (self.df["Close"].iloc[-1] / self.df["Close"].iloc[-50] - 1) * 100
        if getiri50 > 0:
            puan += 5
            nedenler.append("50 günlük yükseliş")

        if puan >= 90:
            trend = "★★★★★ Çok Güçlü"
        elif puan >= 75:
            trend = "★★★★ Güçlü"
        elif puan >= 60:
            trend = "★★★ Orta"
        elif puan >= 40:
            trend = "★★ Zayıf"
        else:
            trend = "★ Çok Zayıf"

        return {
            "TrendSkoru": puan,
            "Trend": trend,
            "ADX": round(adx, 2),
            "DI_PLUS": round(di_plus, 2),
            "DI_MINUS": round(di_minus, 2),
            "EMA20": round(ema20, 2),
            "EMA50": round(ema50, 2),
            "EMA100": round(ema100, 2),
            "EMA200": round(ema200, 2),
            "Getiri20": round(getiri20, 2),
            "Getiri50": round(getiri50, 2),
            "Nedenler": nedenler,
        }
