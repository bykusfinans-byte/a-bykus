# ==========================================================
# BIST AI PRO V2
# MODÜL 03 - GÖSTERGE MOTORU
# ==========================================================

from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator

from settings import Settings


class GostergeMotoru:

    def __init__(self, df):
        self.df = df.copy()

    # ------------------------------------------------------

    def hesapla(self):

        df = self.df

        # ---- EMA ----
        df["EMA20"] = EMAIndicator(close=df["Close"], window=Settings.EMA20).ema_indicator()
        df["EMA50"] = EMAIndicator(close=df["Close"], window=Settings.EMA50).ema_indicator()
        df["EMA100"] = EMAIndicator(close=df["Close"], window=Settings.EMA100).ema_indicator()
        df["EMA200"] = EMAIndicator(close=df["Close"], window=Settings.EMA200).ema_indicator()

        # ---- RSI ----
        df["RSI"] = RSIIndicator(close=df["Close"], window=Settings.RSI).rsi()

        # ---- MACD ----
        macd = MACD(
            close=df["Close"],
            window_fast=Settings.MACD_FAST,
            window_slow=Settings.MACD_SLOW,
            window_sign=Settings.MACD_SIGNAL,
        )
        df["MACD"] = macd.macd()
        df["MACD_SIGNAL"] = macd.macd_signal()
        df["MACD_HIST"] = macd.macd_diff()

        # ---- ADX ----
        adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=Settings.ADX)
        df["ADX"] = adx.adx()
        df["DI_PLUS"] = adx.adx_pos()
        df["DI_MINUS"] = adx.adx_neg()

        # ---- ATR ----
        atr = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=Settings.ATR)
        df["ATR"] = atr.average_true_range()

        # ---- Bollinger ----
        bb = BollingerBands(close=df["Close"], window=Settings.BB)
        df["BB_UPPER"] = bb.bollinger_hband()
        df["BB_MIDDLE"] = bb.bollinger_mavg()
        df["BB_LOWER"] = bb.bollinger_lband()

        # ---- OBV ----
        obv = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"])
        df["OBV"] = obv.on_balance_volume()

        # ---- MFI ----
        mfi = MFIIndicator(
            high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"], window=Settings.MFI
        )
        df["MFI"] = mfi.money_flow_index()

        df = df.dropna().copy()
        self.df = df

        return df
