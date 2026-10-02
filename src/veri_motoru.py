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


def surekliDortSaatlikYap(df):
    """
    Altın/gümüş gibi neredeyse 7/24 işlem gören enstrümanlar için, BIST
    seansına bağlı olmayan standart (kesintisiz) 4 saatlik mumlar üretir.
    """
    df = df.copy()

    gruplu = df.resample("4h").agg(
        {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
    )

    return gruplu.dropna()


class EmtiaVeriMotoru:
    """
    Gram altın/gümüş fiyatını (TL) ons fiyatı (USD) ile USD/TRY kurunu
    çarpıp grama bölerek üretir: (ons_fiyat_usd * usdtry) / 31,1035
    """

    def __init__(self):
        self.cache = {}

    def getir(self, sembol):

        sembol = sembol.upper()

        if sembol in self.cache:
            return self.cache[sembol].copy()

        if sembol not in Settings.EMTIA_TICKERLAR:
            print(f"[HATA] {sembol}: tanımsız emtia sembolü")
            return None

        try:
            ons_ticker = Settings.EMTIA_TICKERLAR[sembol]

            ons = yf.Ticker(ons_ticker).history(
                period=Settings.PERIOD, interval=Settings.INTERVAL, auto_adjust=False
            )
            kur = yf.Ticker(Settings.KUR_TICKER).history(
                period=Settings.PERIOD, interval=Settings.INTERVAL, auto_adjust=False
            )

            if ons.empty or kur.empty:
                raise ValueError("Veri bulunamadı (ons fiyatı veya kur)")

            ortak = ons[["Open", "High", "Low", "Close", "Volume"]].join(
                kur[["Open", "High", "Low", "Close"]], how="inner", lsuffix="_ons", rsuffix="_kur"
            )

            if ortak.empty:
                raise ValueError("Ons fiyatı ve kur verileri zaman olarak eşleşmedi")

            gram = pd.DataFrame(index=ortak.index)
            for kolon in ["Open", "High", "Low", "Close"]:
                gram[kolon] = (ortak[f"{kolon}_ons"] * ortak[f"{kolon}_kur"]) / Settings.ONS_GRAM
            gram["Volume"] = ortak["Volume"]

            gram = gram.dropna()
            gram = surekliDortSaatlikYap(gram)

            if (gram["Volume"] == 0).all():
                gram["Volume"] = 1.0

            if len(gram) < Settings.MIN_BAR:
                raise ValueError(f"Yetersiz veri ({len(gram)} mum)")

            self.cache[sembol] = gram.copy()
            return gram.copy()

        except Exception as e:
            print(f"[HATA] {sembol}: {e}")
            return None


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

            # Bazı semboller (örn. endeksler: XU100, XU030) hacim verisi
            # raporlamaz (hep 0). Bu durumda OBV/MFI gibi hacim bazlı
            # göstergeler sıfıra bölme nedeniyle NaN üretip GostergeMotoru'nun
            # sonundaki dropna() ile TÜM satırları siler. Hacim tamamen
            # sıfırsa, matematiğin patlamaması için nötr bir sabitle (1)
            # dolduruyoruz - bu sembollerde Hacim Skoru çok anlamlı olmaz
            # ama Trend/Momentum/Risk fiyat bazlı olduğu için etkilenmez.
            if (df["Volume"] == 0).all():
                df["Volume"] = 1.0

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
