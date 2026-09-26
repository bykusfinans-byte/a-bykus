# ==========================================================
# BIST AI PRO V2
# MODÜL 05 - MOMENTUM MOTORU
# ==========================================================


class MomentumMotoru:

    def __init__(self, df):
        self.df = df
        self.son = df.iloc[-1]

    # ------------------------------------------------------

    def hesapla(self):

        puan = 0
        nedenler = []

        # RSI
        rsi = self.son["RSI"]

        if 50 <= rsi <= 70:
            puan += 30
            nedenler.append(f"RSI güçlü ({rsi:.2f})")
        elif 40 <= rsi < 50:
            puan += 20
            nedenler.append(f"RSI toparlanıyor ({rsi:.2f})")
        elif rsi > 70:
            puan += 15
            nedenler.append(f"RSI aşırı alım ({rsi:.2f})")
        else:
            nedenler.append(f"RSI zayıf ({rsi:.2f})")

        # MACD
        macd = self.son["MACD"]
        signal = self.son["MACD_SIGNAL"]

        if macd > signal:
            puan += 30
            nedenler.append("MACD AL")
        else:
            nedenler.append("MACD SAT")

        # Histogram
        histogram = self.son["MACD_HIST"]

        if histogram > 0:
            puan += 20
            nedenler.append("Momentum artıyor")
        else:
            nedenler.append("Momentum zayıf")

        # MFI
        mfi = self.son["MFI"]

        if 50 <= mfi <= 80:
            puan += 20
            nedenler.append(f"Para girişi güçlü ({mfi:.2f})")
        elif mfi > 80:
            puan += 10
            nedenler.append(f"Aşırı para girişi ({mfi:.2f})")
        else:
            nedenler.append(f"Para çıkışı ({mfi:.2f})")

        if puan >= 90:
            durum = "★★★★★ Çok Güçlü"
        elif puan >= 75:
            durum = "★★★★ Güçlü"
        elif puan >= 60:
            durum = "★★★ Orta"
        elif puan >= 40:
            durum = "★★ Zayıf"
        else:
            durum = "★ Çok Zayıf"

        return {
            "MomentumSkoru": puan,
            "Momentum": durum,
            "RSI": round(rsi, 2),
            "MACD": round(macd, 2),
            "Signal": round(signal, 2),
            "Histogram": round(histogram, 2),
            "MFI": round(mfi, 2),
            "Nedenler": nedenler,
        }
