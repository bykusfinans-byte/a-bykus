# ==========================================================
# BIST AI PRO V2
# MODÜL 09 - KARAR MOTORU
# ==========================================================

from trend_motoru import TrendMotoru
from momentum_motoru import MomentumMotoru
from hacim_motoru import HacimMotoru
from risk_motoru import RiskMotoru
from teknik_skor_motoru import TeknikSkorMotoru


class KararMotoru:

    def __init__(self, df):
        self.df = df

    # ------------------------------------------------------

    def hesapla(self):

        trend = TrendMotoru(self.df).hesapla()
        momentum = MomentumMotoru(self.df).hesapla()
        hacim = HacimMotoru(self.df).hesapla()
        risk = RiskMotoru(self.df).hesapla()

        teknik = TeknikSkorMotoru(self.df).hesapla()["TeknikSkor"]

        guven = teknik * 0.7 + risk["RiskSkoru"] * 0.3

        if teknik >= 90:
            karar = "🟢🟢 ÇOK GÜÇLÜ AL"
        elif teknik >= 80:
            karar = "🟢 GÜÇLÜ AL"
        elif teknik >= 65:
            karar = "🟡 AL"
        elif teknik >= 50:
            karar = "🟠 TUT"
        else:
            karar = "🔴 SAT"

        return {
            "Karar": karar,
            "Guven": round(guven, 2),
            "TeknikSkor": teknik,
            "Trend": trend,
            "Momentum": momentum,
            "Hacim": hacim,
            "Risk": risk,
        }
