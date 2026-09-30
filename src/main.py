# ==========================================================
# BIST AI PRO V2
# ANA ÇALIŞTIRMA SCRİPTİ
# GitHub Actions bu dosyayı belirli aralıklarla çalıştırır:
#   1) Tüm hisseleri tarar
#   2) Sonuçları docs/data/sonuc.json'a yazar
#   3) Bot'u çalıştırıp portföyü günceller -> docs/data/portfoy.json
# ==========================================================

import json
import os
from datetime import datetime, timezone

import pandas as pd

from settings import Settings
from hisseler import BIST_HISSELERI
from tarama_motoru import BistTaramaMotoru
from emtia_tarama_motoru import EmtiaTaramaMotoru
from bot_motoru import BotMotoru

# Bu dosyanın bulunduğu klasöre göre docs/data yolunu bul
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "docs", "data")
SONUC_PATH = os.path.join(DATA_DIR, "sonuc.json")
EMTIA_PATH = os.path.join(DATA_DIR, "emtia.json")
PORTFOY_PATH = os.path.join(DATA_DIR, "portfoy.json")


def portfoyu_yukle():
    if os.path.exists(PORTFOY_PATH):
        with open(PORTFOY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "nakit": Settings.BOT_BASLANGIC_SERMAYE,
        "baslangic_sermaye": Settings.BOT_BASLANGIC_SERMAYE,
        "pozisyonlar": {},
        "islemler": [],
        "bekleyen": {},
    }


def onceki_sonucu_yukle(path):
    """Bir önceki tarama sonucunu döndürür (varsa) - karşılaştırma için kullanılır."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            eski = json.load(f)
        return eski.get("guncelleme"), eski.get("hisseler", [])
    return None, []


def main():

    os.makedirs(DATA_DIR, exist_ok=True)

    guncelleme_zamani = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1) Hisse taraması
    onceki_guncelleme, onceki_hisseler = onceki_sonucu_yukle(SONUC_PATH)
    tarama_df = BistTaramaMotoru(BIST_HISSELERI).tara()

    sonuc_kaydi = {
        "guncelleme": guncelleme_zamani,
        "hisseler": tarama_df.to_dict(orient="records") if not tarama_df.empty else [],
        "onceki_guncelleme": onceki_guncelleme,
        "onceki_hisseler": onceki_hisseler,
    }

    with open(SONUC_PATH, "w", encoding="utf-8") as f:
        json.dump(sonuc_kaydi, f, ensure_ascii=False, indent=2)

    print(f"Hisse tarama sonucu yazıldı: {SONUC_PATH} ({len(sonuc_kaydi['hisseler'])} hisse)")

    # 2) Emtia taraması (altın/gümüş - temel analiz yok)
    onceki_emtia_guncelleme, onceki_emtia_hisseler = onceki_sonucu_yukle(EMTIA_PATH)
    emtia_df = EmtiaTaramaMotoru().tara()

    emtia_kaydi = {
        "guncelleme": guncelleme_zamani,
        "hisseler": emtia_df.to_dict(orient="records") if not emtia_df.empty else [],
        "onceki_guncelleme": onceki_emtia_guncelleme,
        "onceki_hisseler": onceki_emtia_hisseler,
    }

    with open(EMTIA_PATH, "w", encoding="utf-8") as f:
        json.dump(emtia_kaydi, f, ensure_ascii=False, indent=2)

    print(f"Emtia tarama sonucu yazıldı: {EMTIA_PATH} ({len(emtia_kaydi['hisseler'])} sembol)")

    # 3) Bot - hisse + emtia BİRLEŞİK değerlendirilir (aynı nakit havuzu, aynı kurallar)
    parcalar = [df for df in (tarama_df, emtia_df) if not df.empty]
    birlesik_df = pd.concat(parcalar, ignore_index=True) if parcalar else tarama_df

    if not birlesik_df.empty:
        portfoy = portfoyu_yukle()
        portfoy = BotMotoru(birlesik_df, portfoy).calistir()
        portfoy["guncelleme"] = guncelleme_zamani

        with open(PORTFOY_PATH, "w", encoding="utf-8") as f:
            json.dump(portfoy, f, ensure_ascii=False, indent=2)

        print(f"Portföy güncellendi: {PORTFOY_PATH}")
        print(f"Nakit: {portfoy['nakit']} | Açık pozisyon: {len(portfoy['pozisyonlar'])}")
    else:
        print("Tarama sonucu boş geldi, bot çalıştırılmadı (muhtemelen veri çekme hatası).")


if __name__ == "__main__":
    main()
