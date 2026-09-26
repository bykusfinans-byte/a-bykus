# ==========================================================
# BIST AI PRO V2
# MODÜL 11 - ANALİZ MOTORU
# ==========================================================

from veri_motoru import VeriMotoru
from gosterge_motoru import GostergeMotoru
from trend_motoru import TrendMotoru
from momentum_motoru import MomentumMotoru
from hacim_motoru import HacimMotoru
from risk_motoru import RiskMotoru
from teknik_skor_motoru import TeknikSkorMotoru
from destek_direnc_motoru import DestekDirencMotoru
from temel_analiz_motoru import TemelAnalizMotoru
from karar_motoru import KararMotoru


class AnalizMotoru:

    def __init__(self, hisse, veri_motoru=None):

        self.hisse = hisse.upper()

        veri = veri_motoru or VeriMotoru()
        self.df = veri.getir(self.hisse)

        if self.df is None:
            raise Exception(f"{self.hisse} verisi alınamadı.")

        self.df = GostergeMotoru(self.df).hesapla()

    # ------------------------------------------------------

    def hesapla(self):

        trend = TrendMotoru(self.df).hesapla()
        momentum = MomentumMotoru(self.df).hesapla()
        hacim = HacimMotoru(self.df).hesapla()
        risk = RiskMotoru(self.df).hesapla()
        teknik = TeknikSkorMotoru(self.df).hesapla()
        destek = DestekDirencMotoru(self.df).hesapla()
        temel = TemelAnalizMotoru(self.hisse).puanla()
        karar = KararMotoru(self.df).hesapla()

        return {
            "Hisse": self.hisse,
            "Fiyat": round(self.df.iloc[-1]["Close"], 2),
            "Trend": trend,
            "Momentum": momentum,
            "Hacim": hacim,
            "Risk": risk,
            "Teknik": teknik,
            "Temel": temel,
            "DestekDirenc": destek,
            "Karar": karar,
        }
