# ==========================================================
# BIST AI PRO V2
# MODÜL 17 - BOT MOTORU
# Tarama sonuçlarına bakarak kendi kararını veren, otomatik
# alım/satım yapan sanal (gerçek para kullanmayan) bot.
#
# KURALLAR
# --------
# SERT TETİKLEYİCİLER (anında uygulanır, onay beklemez - risk yönetimi):
#   - Fiyat, hissenin Stop-Loss seviyesine değdiyse       -> SAT (stop)
#   - Fiyat, hissenin Hedef fiyatına ulaştıysa             -> SAT (kâr al)
#
# BREAKEVEN'E ÇEKME:
#   - Fiyat Hedef1'e (giriş + 2×ATR) ulaştıysa, Stop en az giriş
#     fiyatına (maliyete) çekilir. Böylece hedefe ulaşamayıp geri
#     dönen bir pozisyon, kâr varken "zararsız" kapanır - uzak
#     Stop'u bekleyip kârı tamamen geri vermez.
#
# YUMUŞAK SİNYALLER (2 tarama üst üste - yani en az bir sonraki
# tur boyunca - aynı yönde kalırsa uygulanır; tek turluk sıçramaları
# "whipsaw" filtresiyle eler):
#   - AL: AI Skoru >= Settings.BOT_ALIM_ESIGI, hisse elde yok,
#         boş pozisyon slotu var
#   - SAT: AI Skoru < Settings.BOT_SATIM_ESIGI (sinyal bozuldu)
# ==========================================================

from datetime import datetime, timezone

from settings import Settings


class BotMotoru:

    def __init__(self, tarama_df, portfoy):
        """
        tarama_df: BistTaramaMotoru.tara() çıktısı (pandas DataFrame)
        portfoy:   {"nakit": float, "pozisyonlar": {...}, "islemler": [...],
                    "bekleyen": {hisse: "AL"|"SAT_ZAYIF"}}
        """
        self.df = tarama_df
        self.portfoy = portfoy
        self.portfoy.setdefault("bekleyen", {})  # eski portfoy.json dosyalarıyla uyumluluk

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

    def _sinyal_onayla(self, hisse, tip):
        """
        İki turluk onay mekanizması. Aynı sinyal (aynı hisse + aynı tip)
        bir önceki turda da görülmüşse True döner ve bekleyen kaydını
        temizler; ilk kez görülüyorsa sadece kaydedip False döner.
        """
        bekleyen = self.portfoy["bekleyen"]

        if bekleyen.get(hisse) == tip:
            del bekleyen[hisse]
            return True

        bekleyen[hisse] = tip
        return False

    def _sinyal_temizle(self, hisse):
        self.portfoy["bekleyen"].pop(hisse, None)

    # ------------------------------------------------------

    def _sat_uygula(self, hisse, fiyat, gerekce):
        poz = self.portfoy["pozisyonlar"].pop(hisse)
        tutar = round(poz["adet"] * fiyat, 2)
        self.portfoy["nakit"] = round(self.portfoy["nakit"] + tutar, 2)
        self._islem_kaydet(hisse, "SAT", poz["adet"], fiyat, gerekce)
        self._sinyal_temizle(hisse)

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

            # Breakeven'e çekme: Hedef1'e ulaşıldıysa Stop en az maliyete çekilir
            hedef1 = poz.get("hedef1_takip")
            if hedef1 is not None and fiyat >= hedef1:
                yeni_stop = max(poz["stop_takip"], poz["maliyet"])
                if yeni_stop != poz["stop_takip"]:
                    poz["stop_takip"] = yeni_stop

            # Sert tetikleyiciler: onay beklemeden hemen uygulanır
            if fiyat <= poz["stop_takip"]:
                self._sat_uygula(hisse, fiyat, f"Stop-Loss ({poz['stop_takip']})")
                continue

            if fiyat >= poz["hedef_takip"]:
                self._sat_uygula(hisse, fiyat, f"Hedef fiyata ulaşıldı ({poz['hedef_takip']})")
                continue

            # Yumuşak sinyal: AI Skoru düşük - 2 tur üst üste onay gerekir
            if float(satir["AISkor"]) < Settings.BOT_SATIM_ESIGI:
                if self._sinyal_onayla(hisse, "SAT_ZAYIF"):
                    self._sat_uygula(hisse, fiyat, f"AI Skoru 2 tur üst üste düşük ({satir['AISkor']})")
            else:
                self._sinyal_temizle(hisse)  # skor toparladıysa bekleyen kaydını sil

    # ------------------------------------------------------

    def _alislari_uygula(self):

        pozisyonlar = self.portfoy["pozisyonlar"]

        bos_slot = Settings.BOT_MAX_POZISYON - len(pozisyonlar)
        if bos_slot <= 0:
            return

        adaylar = self.df[
            (self.df["AISkor"] >= Settings.BOT_ALIM_ESIGI) & (~self.df["Hisse"].isin(pozisyonlar.keys()))
        ].sort_values("AISkor", ascending=False)

        # Aday olmaktan çıkmış (artık şartı sağlamayan) bekleyen AL kayıtlarını temizle
        gecerli_adaylar = set(adaylar["Hisse"])
        for hisse in list(self.portfoy["bekleyen"].keys()):
            if self.portfoy["bekleyen"][hisse] == "AL" and hisse not in gecerli_adaylar:
                self._sinyal_temizle(hisse)

        # 2 tur üst üste onaylanan adayları belirle (en yüksek skor önce)
        onayli = [satir for _, satir in adaylar.iterrows() if self._sinyal_onayla(satir["Hisse"], "AL")]

        for satir in onayli:

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
                "hedef1_takip": float(satir["Hedef1"]) if "Hedef1" in satir and satir["Hedef1"] is not None else None,
            }

            self._islem_kaydet(
                satir["Hisse"],
                "AL",
                adet,
                fiyat,
                f"AI Skoru 2 tur üst üste >= eşik ({satir['AISkor']}, eşik: {Settings.BOT_ALIM_ESIGI})",
            )

            bos_slot -= 1

    # ------------------------------------------------------

    def calistir(self):
        """Satış kurallarını, sonra alış kurallarını uygular ve güncel portföyü döndürür."""
        self._satislari_uygula()
        self._alislari_uygula()
        return self.portfoy
