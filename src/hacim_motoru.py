# ==========================================================
# BIST AI PRO V2
# MODÜL 06 - HACİM MOTORU
# ==========================================================


class HacimMotoru:

    def __init__(self, df):
        self.df = df
        self.son = df.iloc[-1]

    # ------------------------------------------------------

    def hesapla(self):

        puan = 0
        nedenler = []

        ort_hacim = self.df["Volume"].tail(20).mean()
        son_hacim = self.son["Volume"]
        oran = son_hacim / ort_hacim

        if oran >= 2:
            puan += 30
            nedenler.append("Hacim patlaması")
        elif oran >= 1.5:
            puan += 25
            nedenler.append("Hacim güçlü")
        elif oran >= 1.2:
            puan += 20
            nedenler.append("Hacim ortalamanın üzerinde")
        elif oran >= 1:
            puan += 15
            nedenler.append("Hacim normal")
        else:
            puan += 5
            nedenler.append("Hacim düşük")

        # OBV
        if self.df["OBV"].iloc[-1] > self.df["OBV"].iloc[-5]:
            puan += 35
            nedenler.append("OBV yükseliyor")

        # MFI
        mfi = self.son["MFI"]
        if 50 <= mfi <= 80:
            puan += 25
            nedenler.append(f"Para girişi güçlü ({mfi:.2f})")
        elif mfi > 80:
            puan += 15
            nedenler.append("Aşırı para girişi")
        elif mfi >= 40:
            puan += 10
            nedenler.append("Para girişi zayıf")

        # Fiyat + hacim onayı
        if self.son["Close"] > self.df["Close"].iloc[-2] and son_hacim > ort_hacim:
            puan += 10
            nedenler.append("Yükseliş hacimle destekleniyor")

        puan = min(puan, 100)

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
            "HacimSkoru": puan,
            "Hacim": durum,
            "Nedenler": nedenler,
        }
