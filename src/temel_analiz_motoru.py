# ==========================================================
# BIST AI PRO V2
# MODÜL 14 - TEMEL ANALİZ MOTORU
# ==========================================================

import yfinance as yf


class TemelAnalizMotoru:

    def __init__(self, hisse):
        self.hisse = hisse.upper()
        self.info = yf.Ticker(self.hisse + ".IS").info

    # ------------------------------------------------------

    def puanla(self):

        puan = 0
        nedenler = []

        pe = self.info.get("trailingPE")
        if pe:
            if pe < 10:
                puan += 20
                nedenler.append("F/K düşük")
            elif pe < 20:
                puan += 15
                nedenler.append("F/K makul")
            else:
                puan += 5
                nedenler.append("F/K yüksek")

        pb = self.info.get("priceToBook")
        if pb:
            if pb < 2:
                puan += 15
                nedenler.append("PD/DD iyi")
            elif pb < 4:
                puan += 10
                nedenler.append("PD/DD orta")

        roe = self.info.get("returnOnEquity")
        if roe:
            if roe > 0.20:
                puan += 20
                nedenler.append("ROE güçlü")
            elif roe > 0.10:
                puan += 10
                nedenler.append("ROE orta")

        margin = self.info.get("profitMargins")
        if margin:
            if margin > 0.15:
                puan += 15
                nedenler.append("Karlılık yüksek")
            elif margin > 0.05:
                puan += 10
                nedenler.append("Karlılık orta")

        debt = self.info.get("debtToEquity")
        if debt is not None:
            if debt < 50:
                puan += 15
                nedenler.append("Borç düşük")
            elif debt < 100:
                puan += 10
                nedenler.append("Borç orta")

        dividend = self.info.get("dividendYield")
        if dividend:
            puan += 15
            nedenler.append("Temettü ödüyor")

        puan = min(puan, 100)

        return {
            "TemelSkor": puan,
            "Nedenler": nedenler,
            "PE": pe,
            "PB": pb,
            "ROE": roe,
            "KarMarji": margin,
            "Borc": debt,
            "Temettu": dividend,
        }
