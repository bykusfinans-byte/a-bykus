# ==========================================================
# BIST AI PRO V2
# MODÜL 15 - AI SKOR MOTORU
# ==========================================================

from settings import Settings


class AISkorMotoru:

    def __init__(self, analiz):
        self.analiz = analiz

    # ------------------------------------------------------

    def hesapla(self):

        teknik = self.analiz["Teknik"]["TeknikSkor"]
        temel = self.analiz["Temel"]["TemelSkor"]
        risk = self.analiz["Risk"]["RiskSkoru"]

        ai = teknik * Settings.W_TEKNIK + temel * Settings.W_TEMEL + risk * Settings.W_RISK
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
            "AISkor": ai,
            "Karar": karar,
            "Teknik": teknik,
            "Temel": temel,
            "Risk": risk,
        }
