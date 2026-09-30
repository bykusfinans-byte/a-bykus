# ==========================================================
# BIST AI PRO V2
# MODÜL 18 - EMTİA ANALİZ MOTORU (Altın / Gümüş)
#
# Hisselerden farkı: TEMEL ANALİZ YOK. Bilanço, F/K, ROE gibi
# kavramlar bir emtia için anlamsız. AI Skoru sadece Teknik ve
# Risk'ten oluşuyor.
# ==========================================================

from settings import Settings
from veri_motoru import EmtiaVeriMotoru
from gosterge_motoru import GostergeMotoru
from trend_motoru import TrendMotoru
from momentum_motoru import MomentumMotoru
from hacim_motoru import HacimMotoru
from risk_motoru import RiskMotoru
from teknik_skor_motoru import TeknikSkorMotoru
from destek_direnc_motoru import DestekDirencMotoru
from filtre_motoru import FiltreMotoru


class EmtiaAnalizMotoru:

    def __init__(self, sembol, veri_motoru=None):

        self.sembol = sembol.upper()

        veri = veri_motoru or EmtiaVeriMotoru()
        self.df = veri.getir(self.sembol)

        if self.df is None:
            raise Exception(f"{self.sembol} verisi alınamadı.")

        self.df = GostergeMotoru(self.df).hesapla()

    # ------------------------------------------------------

    def hesapla(self):

        trend = TrendMotoru(self.df).hesapla()
        momentum = MomentumMotoru(self.df).hesapla()
        hacim = HacimMotoru(self.df).hesapla()
        risk = RiskMotoru(self.df).hesapla()
        teknik = TeknikSkorMotoru(self.df).hesapla()
        destek = DestekDirencMotoru(self.df).hesapla()
        filtre = FiltreMotoru(self.df).hesapla()

        ai = teknik["TeknikSkor"] * Settings.W_TEKNIK_EMTIA + risk["RiskSkoru"] * Settings.W_RISK_EMTIA
        ai = round(ai, 2)

        if ai >= 90:
            karar = "★★★★★ ÇOK GÜÇLÜ AL"
        elif ai >= 80:
            karar = "★★★★ GÜÇLÜ AL"
        elif ai >= 70:
            karar = "★★★ AL"
        elif ai >= 60:
            karar = "★★ TUT"
        elif ai >= 50:
            karar = "★ ZAYIF"
        else:
            karar = "🔴 SAT"

        return {
            "Hisse": self.sembol,
            "Fiyat": round(self.df.iloc[-1]["Close"], 2),
            "Trend": trend,
            "Momentum": momentum,
            "Hacim": hacim,
            "Risk": risk,
            "Teknik": teknik,
            "DestekDirenc": destek,
            "Filtre": filtre,
            "AISkor": ai,
            "Karar": karar,
        }
