# ==========================================================
# BIST AI PRO V2
# MODÜL 19 - EMTİA TARAMA MOTORU
# ==========================================================

import time

import pandas as pd

from settings import Settings
from veri_motoru import EmtiaVeriMotoru
from emtia_analiz_motoru import EmtiaAnalizMotoru

EMTIA_SEMBOLLERI = ["ALTIN", "GUMUS"]


class EmtiaTaramaMotoru:

    def tara(self):

        sonuc = []
        veri = EmtiaVeriMotoru()

        print("=" * 70)
        print("EMTİA (ALTIN/GÜMÜŞ) TARAMASI BAŞLADI")
        print("=" * 70)

        for sembol in EMTIA_SEMBOLLERI:

            print(f"{sembol} analiz ediliyor...")

            try:
                analiz = EmtiaAnalizMotoru(sembol, veri_motoru=veri).hesapla()

                sonuc.append(
                    {
                        "Hisse": analiz["Hisse"],
                        "Fiyat": analiz["Fiyat"],
                        "Trend": analiz["Trend"]["Trend"],
                        "TrendSkor": analiz["Trend"]["TrendSkoru"],
                        "Momentum": analiz["Momentum"]["Momentum"],
                        "MomentumSkor": analiz["Momentum"]["MomentumSkoru"],
                        "Teknik": analiz["Teknik"]["TeknikSkor"],
                        "Temel": None,  # emtiada temel analiz yok
                        "Risk": analiz["Risk"]["RiskSkoru"],
                        "AISkor": analiz["AISkor"],
                        "Karar": analiz["Karar"],
                        "RSI": analiz["Momentum"]["RSI"],
                        "MACD": analiz["Momentum"]["MACD"],
                        "ADX": analiz["Trend"]["ADX"],
                        "ATR": analiz["Risk"]["ATR"],
                        "EMA9": analiz["Filtre"]["EMA9"],
                        "EMA21": analiz["Filtre"]["EMA21"],
                        "SMA50": analiz["Filtre"]["SMA50"],
                        "SMA200": analiz["Filtre"]["SMA200"],
                        "FiltreGecti": analiz["Filtre"]["Gecti"],
                        "Destek": analiz["DestekDirenc"]["Destek20"],
                        "Direnc": analiz["DestekDirenc"]["Direnc20"],
                        "Stop": analiz["Risk"]["StopLoss"],
                        "Hedef1": analiz["Risk"]["Hedef1"],
                        "Hedef": analiz["Risk"]["HedefFiyat"],
                        "Risk/Odul": analiz["Risk"]["RiskOdul"],
                    }
                )

            except Exception as e:
                print(f"HATA -> {sembol}: {e}")

            time.sleep(Settings.SLEEP)

        df = pd.DataFrame(sonuc)

        if not df.empty:
            df = df.sort_values("AISkor", ascending=False)
            df.reset_index(drop=True, inplace=True)

        return df
