# ==========================================================
# BIST AI PRO V2
# MODÜL 10 - DESTEK DİRENÇ MOTORU
# ==========================================================


class DestekDirencMotoru:

    def __init__(self, df):
        self.df = df

    def hesapla(self):

        son = self.df.iloc[-1]

        destek20 = self.df["Low"].tail(20).min()
        destek50 = self.df["Low"].tail(50).min()

        direnc20 = self.df["High"].tail(20).max()
        direnc50 = self.df["High"].tail(50).max()

        pivot = (son["High"] + son["Low"] + son["Close"]) / 3

        r1 = pivot * 2 - son["Low"]
        s1 = pivot * 2 - son["High"]

        r2 = pivot + (son["High"] - son["Low"])
        s2 = pivot - (son["High"] - son["Low"])

        return {
            "Destek20": round(destek20, 2),
            "Destek50": round(destek50, 2),
            "Direnc20": round(direnc20, 2),
            "Direnc50": round(direnc50, 2),
            "Pivot": round(pivot, 2),
            "R1": round(r1, 2),
            "R2": round(r2, 2),
            "S1": round(s1, 2),
            "S2": round(s2, 2),
        }
