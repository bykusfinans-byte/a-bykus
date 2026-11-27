# Borsa verilerini Yahoo Finance'ten çekip docs/data/ klasörüne JSON olarak yazar.
# Sembol listesini docs/borsa-paneli.html içindeki SYMS bölümünden okur.
import json, re, os, datetime
import pandas as pd
import yfinance as yf

html = open("docs/borsa-paneli.html", encoding="utf-8").read()
blk = html.split("const SYMS={")[1].split("function conv")[0]
syms = re.findall(r'\b([A-Z0-9]{3,7}):\[', blk)
OUT = "docs/data"
os.makedirs(OUT, exist_ok=True)

SPECIAL = {"XU100": "XU100.IS", "USDTRY": "USDTRY=X", "GAU": "GC=F", "GAG": "SI=F"}
tick = lambda s: SPECIAL.get(s, s + ".IS")

def get(t, period, interval):
    df = yf.download(t, period=period, interval=interval, auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna(subset=["Open", "High", "Low", "Close"])

def rows(df, fmt="%Y-%m-%d"):
    return [[i.strftime(fmt), round(float(r.Open), 3), round(float(r.High), 3),
             round(float(r.Low), 3), round(float(r.Close), 3), int(r.Volume or 0)]
            for i, r in df.iterrows()]

def save(name, data):
    with open(f"{OUT}/{name}.json", "w") as f:
        json.dump(data, f, separators=(",", ":"))

usd = get("USDTRY=X", "3y", "1d")["Close"]

def four_hour(df):
    # BIST saatlik mumlarını 10:00 ve 14:00 başlangıçlı iki mumda toplar.
    out = {}
    for i, r in df.iterrows():
        b = 0 if i.hour < 14 else 1
        k = (i.strftime("%Y-%m-%d"), b)
        if k not in out:
            out[k] = [r.Open, r.High, r.Low, r.Close, r.Volume]
        else:
            o = out[k]
            o[1] = max(o[1], r.High); o[2] = min(o[2], r.Low); o[3] = r.Close; o[4] += r.Volume
    res = []
    for (d, b), v in sorted(out.items()):
        t = int(pd.Timestamp(f"{d} {10 if b == 0 else 14}:00", tz="UTC").timestamp())
        res.append([t, round(float(v[0]), 3), round(float(v[1]), 3),
                    round(float(v[2]), 3), round(float(v[3]), 3), int(v[4] or 0)])
    return res

ok = 0
for s in syms:
    try:
        df = get(tick(s), "3y", "1d")
        if s in ("GAU", "GAG"):  # ons (USD) -> gram (TL)
            k = usd.reindex(df.index, method="ffill")
            for c in ("Open", "High", "Low", "Close"):
                df[c] = df[c] * k / 31.1035
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
        if df.empty:
            raise ValueError("veri yok")
        save(s, rows(df))
        ok += 1
        if s not in SPECIAL or s == "XU100":
            try:
                h = get(tick(s), "730d", "60m")
                if not h.empty:
                    save(s + "_4h", four_hour(h))
            except Exception as e:
                print(s, "4s hata:", e)
    except Exception as e:
        print(s, "hata:", e)

with open(f"{OUT}/meta.json", "w") as f:
    json.dump({"updated": datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M UTC")}, f)
print(f"{ok}/{len(syms)} sembol yazildi")
