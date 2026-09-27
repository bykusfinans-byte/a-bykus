# ==========================================================
# BIST AI PRO V2
# MODÜL 17 - BOT MOTORU
# Tarama sonuçlarına bakarak kendi kararını veren, otomatik
# alım/satım yapan sanal (gerçek para kullanmayan) bot.
#
# KURALLAR
# --------
# SATIŞ (önce kontrol edilir):
#   - Fiyat, hissenin Stop-Loss seviyesine değdiyse       -> SAT (stop)
#   - Fiyat, hissenin Hedef fiyatına ulaştıysa             -> SAT (kâr al)
#   - AI Skoru, Settings.BOT_SATIM_ESIGI altına düştüyse   -> SAT (sinyal bozuldu)
#
# ALIŞ:
#   - AI Skoru >= Settings.BOT_ALIM_ESIGI
#   - Hisse zaten portföyde değil
#   - Açık pozisyon sayısı Settings.BOT_MAX_POZISYON'u aşmıyor
#   - Boş slotlara eşit ağırlıklı nakit dağıtılır
# ==========================================================

from datetime import datetime, timezone

from settings import Settings


class BotMotoru:

    def __init__(self, tarama_df, portfoy):
        """
        tarama_df: BistTaramaMotoru.tara() çıktısı (pandas DataFrame)
        portfoy:   {"nakit": float, "pozisyonlar": {hisse: {...}}, "islemler": [...]}
        """
        self.df = tarama_df
        self.portfoy = portfoy

    # ------------------------------------------------------

    def _satir(self, hisse):
        eslesen = self.df[self.df["Hisse"] == hisse]
        if eslesen.empty:
            return None
        return eslesen.iloc[0]

    # ------------------------------------------------------

    def _islem_kaydet(self, hisse, tip, adet, fiyat, gerekce):
        self.portfoy["islemler"].append(
            {
                "tarih": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "hisse": hisse,
                "tip": tip,
                "adet": adet,
                "fiyat": fiyat,
                "tutar": round(adet * fiyat, 2),
                "gerekce": gerekce,
            }
        )

    # ------------------------------------------------------

    def _satislari_uygula(self):

        pozisyonlar = self.portfoy["pozisyonlar"]

        for hisse in list(pozisyonlar.keys()):

            satir = self._satir(hisse)

            if satir is None:
                # Hisse bu taramada bulunamadı (veri hatası vb.) - dokunma
                continue

            fiyat = float(satir["Fiyat"])
            poz = pozisyonlar[hisse]

            sat = False
            gerekce = ""

            if fiyat <= poz["stop_takip"]:
                sat = True
                gerekce = f"Stop-Loss ({poz['stop_takip']})"
            elif fiyat >= poz["hedef_takip"]:
                sat = True
                gerekce = f"Hedef fiyata ulaşıldı ({poz['hedef_takip']})"
            elif float(satir["AISkor"]) < Settings.BOT_SATIM_ESIGI:
                sat = True
                gerekce = f"AI Skoru düştü ({satir['AISkor']})"

            if sat:
                adet = poz["adet"]
                tutar = round(adet * fiyat, 2)
                self.portfoy["nakit"] = round(self.portfoy["nakit"] + tutar, 2)
                self._islem_kaydet(hisse, "SAT", adet, fiyat, gerekce)
                del pozisyonlar[hisse]

    # ------------------------------------------------------

    def _alislari_uygula(self):

        pozisyonlar = self.portfoy["pozisyonlar"]

        bos_slot = Settings.BOT_MAX_POZISYON - len(pozisyonlar)
        if bos_slot <= 0:
            return

        adaylar = self.df[
            (self.df["AISkor"] >= Settings.BOT_ALIM_ESIGI) & (~self.df["Hisse"].isin(pozisyonlar.keys()))
        ].sort_values("AISkor", ascending=False)

        for _, satir in adaylar.iterrows():

            if bos_slot <= 0 or self.portfoy["nakit"] <= 0:
                break

            fiyat = float(satir["Fiyat"])
            pay = self.portfoy["nakit"] / bos_slot
            adet = int(pay // fiyat)

            if adet < 1:
                continue

            tutar = round(adet * fiyat, 2)
            self.portfoy["nakit"] = round(self.portfoy["nakit"] - tutar, 2)

            pozisyonlar[satir["Hisse"]] = {
                "adet": adet,
                "maliyet": fiyat,
                "tarih": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "stop_takip": float(satir["Stop"]),
                "hedef_takip": float(satir["Hedef"]),
            }

            self._islem_kaydet(
                satir["Hisse"], "AL", adet, fiyat, f"AI Skoru {satir['AISkor']} (eşik: {Settings.BOT_ALIM_ESIGI})"
            )

            bos_slot -= 1

    # ------------------------------------------------------

    def calistir(self):
        """Satış kurallarını, sonra alış kurallarını uygular ve güncel portföyü döndürür."""
        self._satislari_uygula()
        self._alislari_uygula()
        return self.portfoy
