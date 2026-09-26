# ==========================================================
# BIST AI PRO V2
# MODÜL 07 - TEKNİK SKOR MOTORU
# ==========================================================

from settings import Settings
from trend_motoru import TrendMotoru
from momentum_motoru import MomentumMotoru
from hacim_motoru import HacimMotoru


class TeknikSkorMotoru:

    def __init__(self, df):
        self.df = df

    # ------------------------------------------------------

    def hesapla(self):

        trend = TrendMotoru(self.df).hesapla()
        momentum = MomentumMotoru(self.df).hesapla()
        hacim = HacimMotoru(self.df).hesapla()

        teknik = (
            trend["TrendSkoru"] * Settings.W_TREND
            + momentum["MomentumSkoru"] * Settings.W_MOMENTUM
            + hacim["HacimSkoru"] * Settings.W_HACIM
        )

        return {
            "Trend": trend,
            "Momentum": momentum,
            "Hacim": hacim,
            "TeknikSkor": round(teknik, 2),
        }
