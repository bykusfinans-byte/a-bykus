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

from settings import Settings
from hisseler import BIST_HISSELERI
from tarama_motoru import BistTaramaMotoru
from bot_motoru import BotMotoru

# Bu dosyanın bulunduğu klasöre göre docs/data yolunu bul
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "docs", "data")
SONUC_PATH = os.path.join(DATA_DIR, "sonuc.json")
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


def onceki_sonucu_yukle():
    """Bir önceki tarama sonucunu döndürür (varsa) - karşılaştırma için kullanılır."""
    if os.path.exists(SONUC_PATH):
        with open(SONUC_PATH, "r", encoding="utf-8") as f:
            eski = json.load(f)
        return eski.get("guncelleme"), eski.get("hisseler", [])
    return None, []


def main():

    os.makedirs(DATA_DIR, exist_ok=True)

    onceki_guncelleme, onceki_hisseler = onceki_sonucu_yukle()

    # 1) Tarama
    tarama_df = BistTaramaMotoru(BIST_HISSELERI).tara()

    guncelleme_zamani = datetime.now(timezone.utc).isoformat(timespec="seconds")

    sonuc_kaydi = {
        "guncelleme": guncelleme_zamani,
        "hisseler": tarama_df.to_dict(orient="records") if not tarama_df.empty else [],
        "onceki_guncelleme": onceki_guncelleme,
        "onceki_hisseler": onceki_hisseler,
    }

    with open(SONUC_PATH, "w", encoding="utf-8") as f:
        json.dump(sonuc_kaydi, f, ensure_ascii=False, indent=2)

    print(f"Tarama sonucu yazıldı: {SONUC_PATH} ({len(sonuc_kaydi['hisseler'])} hisse)")

    # 2) Bot - otomatik alım/satım
    if not tarama_df.empty:
        portfoy = portfoyu_yukle()
        portfoy = BotMotoru(tarama_df, portfoy).calistir()
        portfoy["guncelleme"] = guncelleme_zamani

        with open(PORTFOY_PATH, "w", encoding="utf-8") as f:
            json.dump(portfoy, f, ensure_ascii=False, indent=2)

        print(f"Portföy güncellendi: {PORTFOY_PATH}")
        print(f"Nakit: {portfoy['nakit']} | Açık pozisyon: {len(portfoy['pozisyonlar'])}")
    else:
        print("Tarama sonucu boş geldi, bot çalıştırılmadı (muhtemelen veri çekme hatası).")


if __name__ == "__main__":
    main()
