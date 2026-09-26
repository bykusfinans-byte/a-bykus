# ==========================================================
# BIST AI PRO V2
# MODÜL 12 - TARAMA MOTORU
# ==========================================================

import time

import pandas as pd

from settings import Settings
from veri_motoru import VeriMotoru
from analiz_motoru import AnalizMotoru
from ai_skor_motoru import AISkorMotoru


class BistTaramaMotoru:

    def __init__(self, hisseler):
        self.hisseler = hisseler

    # ------------------------------------------------------

    def tara(self):

        sonuc = []
        veri = VeriMotoru()  # tüm taramada tek VeriMotoru -> cache paylaşılır

        print("=" * 70)
        print("BIST AI PRO V2 TARAMA BAŞLADI")
        print("=" * 70)

        for i, hisse in enumerate(self.hisseler):

            print(f"[{i + 1}/{len(self.hisseler)}] {hisse} analiz ediliyor...")

            try:
                # Not: AnalizMotoru.hesapla() temel analizi de içeride hesaplar,
                # bu yüzden burada TemelAnalizMotoru'nu AYRICA çağırmıyoruz
                # (önceki sürümde bu veri yfinance'tan 2 kere çekiliyordu).
                analiz = AnalizMotoru(hisse, veri_motoru=veri).hesapla()

                ai = AISkorMotoru(analiz).hesapla()

                sonuc.append(
                    {
                        "Hisse": analiz["Hisse"],
                        "Fiyat": analiz["Fiyat"],
                        "Trend": analiz["Trend"]["Trend"],
                        "TrendSkor": analiz["Trend"]["TrendSkoru"],
                        "Momentum": analiz["Momentum"]["Momentum"],
                        "MomentumSkor": analiz["Momentum"]["MomentumSkoru"],
                        "Teknik": analiz["Teknik"]["TeknikSkor"],
                        "Temel": analiz["Temel"]["TemelSkor"],
                        "Risk": analiz["Risk"]["RiskSkoru"],
                        "AISkor": ai["AISkor"],
                        "Karar": ai["Karar"],
                        "RSI": analiz["Momentum"]["RSI"],
                        "ADX": analiz["Trend"]["ADX"],
                        "ATR": analiz["Risk"]["ATR"],
                        "Destek": analiz["DestekDirenc"]["Destek20"],
                        "Direnc": analiz["DestekDirenc"]["Direnc20"],
                        "Stop": analiz["Risk"]["StopLoss"],
                        "Hedef": analiz["Risk"]["HedefFiyat"],
                        "Risk/Odul": analiz["Risk"]["RiskOdul"],
                    }
                )

            except Exception as e:
                print(f"HATA -> {hisse}: {e}")

            time.sleep(Settings.SLEEP)

        df = pd.DataFrame(sonuc)

        if not df.empty:
            df = df.sort_values("AISkor", ascending=False)
            df.reset_index(drop=True, inplace=True)

        return df
