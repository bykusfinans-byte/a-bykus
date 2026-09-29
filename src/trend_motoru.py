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

        ema9 = self.son["EMA9"]
        ema21 = self.son["EMA21"]
        ema50 = self.son["EMA50"]

        adx = self.son["ADX"]
        di_plus = self.son["DI_PLUS"]
        di_minus = self.son["DI_MINUS"]

        fiyat = self.son["Close"]

        # EMA dizilimi (kısa/orta vade - 4 saatlik sisteme göre)
        if ema9 > ema21:
            puan += 20
            nedenler.append("EMA9 > EMA21")

        if ema21 > ema50:
            puan += 20
            nedenler.append("EMA21 > EMA50")

        # Fiyat EMA üzerinde mi?
        if fiyat > ema9:
            puan += 15
            nedenler.append("Fiyat EMA9 üzerinde")

        if fiyat > ema21:
            puan += 10
            nedenler.append("Fiyat EMA21 üzerinde")

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

        # 20 mum (yaklaşık 10 işlem günü) getirisi
        getiri20 = (self.df["Close"].iloc[-1] / self.df["Close"].iloc[-20] - 1) * 100
        if getiri20 > 0:
            puan += 5
            nedenler.append("Son 20 mumda yükseliş")

        # 50 mum (yaklaşık 25 işlem günü) getirisi
        getiri50 = (self.df["Close"].iloc[-1] / self.df["Close"].iloc[-50] - 1) * 100
        if getiri50 > 0:
            puan += 5
            nedenler.append("Son 50 mumda yükseliş")

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
            "EMA9": round(ema9, 2),
            "EMA21": round(ema21, 2),
            "EMA50": round(ema50, 2),
            "Getiri20": round(getiri20, 2),
            "Getiri50": round(getiri50, 2),
            "Nedenler": nedenler,
        }
