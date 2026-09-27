# ==========================================================
# BIST AI PRO V2
# MODÜL 02 - VERİ MOTORU
# ==========================================================

import yfinance as yf

from settings import Settings


class VeriMotoru:

    def __init__(self):
        self.cache = {}

    # ------------------------------------------------------

    def getir(self, hisse):

        hisse = hisse.upper()

        if hisse in self.cache:
            return self.cache[hisse].copy()

        try:
            ticker = yf.Ticker(hisse + ".IS")

            df = ticker.history(period=Settings.PERIOD, auto_adjust=False)

            if df.empty:
                raise ValueError("Veri bulunamadı")

            if "Adj Close" in df.columns:
                df.drop(columns=["Adj Close"], inplace=True)

            for col in ["Dividends", "Stock Splits", "Capital Gains"]:
                if col in df.columns:
                    df.drop(columns=col, inplace=True)

            df = df.dropna()

            if len(df) < Settings.MIN_BAR:
                raise ValueError(f"Yetersiz veri ({len(df)} satır)")

            df = df.sort_index()

            self.cache[hisse] = df.copy()

            return df.copy()

        except Exception as e:
            print(f"[HATA] {hisse}: {e}")
            return None

    # ------------------------------------------------------

    def cache_temizle(self):
        self.cache.clear()

    # ------------------------------------------------------

    def cache_bilgisi(self):
        return list(self.cache.keys())
