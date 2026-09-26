# ==========================================================
# BIST AI PRO V2
# MODÜL 08 - RİSK MOTORU
# ==========================================================

from settings import Settings


class RiskMotoru:

    def __init__(self, df):
        self.df = df
        self.son = df.iloc[-1]

    # ------------------------------------------------------

    def hesapla(self):

        nedenler = []

        fiyat = self.son["Close"]
        atr = self.son["ATR"]

        atr_oran = (atr / fiyat) * 100

        puan = 100

        if atr_oran > 8:
            puan -= 50
            nedenler.append("Çok yüksek volatilite")
        elif atr_oran > 6:
            puan -= 35
            nedenler.append("Yüksek volatilite")
        elif atr_oran > 4:
            puan -= 20
            nedenler.append("Orta volatilite")
        elif atr_oran > 2:
            puan -= 10
            nedenler.append("Normal volatilite")
        else:
            nedenler.append("Düşük volatilite")

        stop = fiyat - atr * Settings.ATR_STOP
        hedef1 = fiyat + atr * Settings.ATR_TARGET1
        hedef2 = fiyat + atr * Settings.ATR_TARGET2
        hedef3 = fiyat + atr * Settings.ATR_TARGET3

        risk = fiyat - stop
        odul = hedef2 - fiyat
        rr = odul / risk if risk > 0 else 0

        if puan >= 90:
            seviye = "Çok Düşük"
        elif puan >= 75:
            seviye = "Düşük"
        elif puan >= 60:
            seviye = "Orta"
        elif puan >= 40:
            seviye = "Yüksek"
        else:
            seviye = "Çok Yüksek"

        return {
            "RiskSkoru": round(puan, 2),
            "RiskSeviyesi": seviye,
            "Risk": seviye,
            "ATR": round(atr, 2),
            "ATR%": round(atr_oran, 2),
            "StopLoss": round(stop, 2),
            "HedefFiyat": round(hedef2, 2),
            "Hedef1": round(hedef1, 2),
            "Hedef2": round(hedef2, 2),
            "Hedef3": round(hedef3, 2),
            "RiskOdul": round(rr, 2),
            "Nedenler": nedenler,
        }
