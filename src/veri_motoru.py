# ==========================================================
# BIST AI PRO V2
# MODÜL 02 - VERİ MOTORU
# ==========================================================

import yfinance as yf
import numpy as np
import pandas as pd

from settings import Settings


def dortSaatlikYap(df):
    """
    yfinance'tan gelen 1 saatlik BIST verisini, seans saatlerine göre
    (10:00-14:00 ve 14:00-18:00) 4 saatlik mumlara birleştirir.
    """

    df = df.copy()

    if df.index.tz is None:
        df.index = df.index.tz_localize("Europe/Istanbul")
    else:
        df.index = df.index.tz_convert("Europe/Istanbul")

    saat = df.index.hour
    dilim_saati = np.where(saat < 14, "10:00:00", "14:00:00")

    df["_gun"] = df.index.date
    df["_dilim"] = dilim_saati

    gruplu = df.groupby(["_gun", "_dilim"]).agg(
        Open=("Open", "first"),
        High=("High", "max"),
        Low=("Low", "min"),
        Close=("Close", "last"),
        Volume=("Volume", "sum"),
    )

    yeni_index = [
        pd.Timestamp(f"{gun} {dilim}", tz="Europe/Istanbul") for gun, dilim in gruplu.index
    ]
    gruplu.index = pd.DatetimeIndex(yeni_index)
    gruplu = gruplu.sort_index()

    return gruplu


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

            df = ticker.history(period=Settings.PERIOD, interval=Settings.INTERVAL, auto_adjust=False)

            if df.empty:
                raise ValueError("Veri bulunamadı")

            if "Adj Close" in df.columns:
                df.drop(columns=["Adj Close"], inplace=True)

            for col in ["Dividends", "Stock Splits", "Capital Gains"]:
                if col in df.columns:
                    df.drop(columns=col, inplace=True)

            df = df.dropna()
            df = dortSaatlikYap(df)  # saatlik veriyi 4 saatlik mumlara birleştir

            if len(df) < Settings.MIN_BAR:
                raise ValueError(f"Yetersiz veri ({len(df)} mum)")

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
