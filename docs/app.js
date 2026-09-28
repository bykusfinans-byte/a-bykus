// ==========================================================
// BIST AI PRO V2 - Frontend
// ==========================================================
//
// ÖNEMLİ: Buradaki şifre koruması sadece rastgele ziyaretçileri
// uzak tutmak içindir. GitHub Pages'teki tüm dosyalar (data/*.json
// dahil) herkese açık ve indirilebilir durumdadır - gerçek bir
// güvenlik önlemi DEĞİLDİR. Repoyu tamamen gizli tutmak istersen
// GitHub'ın ücretli planındaki "private repo + Pages" özelliğini
// kullanman gerekir.
//
// Şifreyi değiştirmek için:
//   1) Tarayıcı konsolunda şunu çalıştır:
//      await crypto.subtle.digest("SHA-256", new TextEncoder().encode("YENİ_ŞİFREN"))
//        .then(b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2,"0")).join(""))
//   2) Çıkan uzun metni aşağıdaki SIFRE_HASH değerine yapıştır.
// ==========================================================

const SIFRE_HASH = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"; // varsayılan: "1234"

// ----------------------------------------------------------
// GitHub Actions'ı tetiklemek için ayarlar
// ----------------------------------------------------------
// Token'ı buraya YAZMIYORUZ — GitHub, public repolara token commit
// edilmesini "secret scanning" ile zaten engelliyor (haklı olarak,
// commit geçmişine giren token'lar botlarca taranıp ele geçirilebiliyor).
// Bunun yerine token, sadece SENİN tarayıcında (localStorage) saklanır,
// koda hiç karışmaz. İlk "Yeni Tarama Başlat" tıklamanda senden istenir.
const GITHUB_OWNER = "bykusfinans-byte";
const GITHUB_REPO = "a-bykus";
const GITHUB_WORKFLOW_FILE = "tarama.yml";
const GITHUB_BRANCH = "main";
const TOKEN_ANAHTARI = "bist-ai-pro-github-token";

function tokenGetir() {
  return localStorage.getItem(TOKEN_ANAHTARI) || "";
}

function tokenIste() {
  return new Promise((resolve) => {
    const modal = document.getElementById("token-modal");
    const input = document.getElementById("token-input");
    const kaydetBtn = document.getElementById("token-kaydet-buton");
    const iptalBtn = document.getElementById("token-iptal-buton");

    input.value = "";
    modal.classList.remove("gizli");
    input.focus();

    function temizle() {
      modal.classList.add("gizli");
      kaydetBtn.removeEventListener("click", kaydetOl);
      iptalBtn.removeEventListener("click", iptalOl);
      input.removeEventListener("keydown", enterOl);
    }

    function kaydetOl() {
      const deger = input.value.trim();
      temizle();
      if (deger) {
        localStorage.setItem(TOKEN_ANAHTARI, deger);
        resolve(deger);
      } else {
        resolve(null);
      }
    }

    function iptalOl() {
      temizle();
      resolve(null);
    }

    function enterOl(e) {
      if (e.key === "Enter") kaydetOl();
    }

    kaydetBtn.addEventListener("click", kaydetOl);
    iptalBtn.addEventListener("click", iptalOl);
    input.addEventListener("keydown", enterOl);
  });
}

let sonGuncellemeZamani = null;
let bekleyenInterval = null;

async function sha256(metin) {
  const buffer = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(metin));
  return [...new Uint8Array(buffer)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

const kilitEkrani = document.getElementById("kilit-ekrani");
const uygulama = document.getElementById("uygulama");
const sifreInput = document.getElementById("sifre-input");
const sifreButon = document.getElementById("sifre-buton");
const sifreHata = document.getElementById("sifre-hata");

async function girisDene() {
  const girilen = sifreInput.value;
  const hash = await sha256(girilen);

  if (hash === SIFRE_HASH) {
    sessionStorage.setItem("bist-ai-pro-giris", "ok");
    kilitEkrani.classList.add("gizli");
    uygulama.classList.remove("gizli");
    veriYukle();
  } else {
    sifreHata.textContent = "Şifre yanlış, tekrar dene.";
  }
}

sifreButon.addEventListener("click", girisDene);
sifreInput.addEventListener("keydown", (e) => { if (e.key === "Enter") girisDene(); });

document.getElementById("kilitle-buton").addEventListener("click", () => {
  sessionStorage.removeItem("bist-ai-pro-giris");
  location.reload();
});

document.getElementById("yenile-buton").addEventListener("click", veriYukle);
document.getElementById("tarama-buton").addEventListener("click", taramaBaslat);
document.getElementById("token-buton").addEventListener("click", async () => {
  localStorage.removeItem(TOKEN_ANAHTARI);
  await tokenIste();
});

// Bu tarayıcı oturumunda zaten giriş yapılmışsa şifreyi tekrar sorma
if (sessionStorage.getItem("bist-ai-pro-giris") === "ok") {
  kilitEkrani.classList.add("gizli");
  uygulama.classList.remove("gizli");
  veriYukle();
}

// ----------------------------------------------------------
// Veri çekme ve tabloları doldurma
// ----------------------------------------------------------

function paraFormat(sayi) {
  if (sayi === null || sayi === undefined || isNaN(sayi)) return "—";
  return sayi.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " ₺";
}

function kzSinifi(sayi) {
  return sayi > 0 ? "pozitif" : sayi < 0 ? "negatif" : "";
}

async function veriYukle() {
  try {
    const [sonucRes, portfoyRes] = await Promise.all([
      fetch("data/sonuc.json?_=" + Date.now()),
      fetch("data/portfoy.json?_=" + Date.now()),
    ]);

    const sonuc = sonucRes.ok ? await sonucRes.json() : { guncelleme: null, hisseler: [] };
    const portfoy = portfoyRes.ok ? await portfoyRes.json() : null;

    document.getElementById("guncelleme-zamani").textContent = sonuc.guncelleme
      ? "Son güncelleme: " + new Date(sonuc.guncelleme).toLocaleString("tr-TR")
      : "Henüz tarama yapılmadı";
    document.getElementById("guncelleme-zamani").style.color = "";

    sonGuncellemeZamani = sonuc.guncelleme;

    sinyalTablosunuDoldur(sonuc.hisseler || []);
    filtreTablosunuDoldur(sonuc.hisseler || []);

    sonBilinenFiyatlar = Object.fromEntries((sonuc.hisseler || []).map((h) => [h.Hisse, h.Fiyat]));
    await manuelGoster();

    if (portfoy) {
      portfoyOzetiDoldur(portfoy, sonuc.hisseler || []);
      pozisyonTablosunuDoldur(portfoy, sonuc.hisseler || []);
      islemTablosunuDoldur(portfoy.islemler || []);
    }
  } catch (err) {
    console.error("Veri yüklenemedi:", err);
    const el = document.getElementById("guncelleme-zamani");
    el.textContent = "Veri yüklenemedi (konsolu kontrol et: F12)";
    el.style.color = "var(--neg)";
  }
}

function sinyalTablosunuDoldur(hisseler) {
  const gövde = document.querySelector("#sinyal-tablo tbody");

  if (!hisseler.length) {
    gövde.innerHTML = '<tr><td colspan="17" class="bos-satir">Henüz tarama verisi yok. İlk GitHub Actions çalıştığında burası dolacak.</td></tr>';
    return;
  }

  gövde.innerHTML = hisseler
    .map(
      (h) => `
    <tr>
      <td>${h.Hisse}</td>
      <td>${paraFormat(h.Fiyat)}</td>
      <td>${h.AISkor ?? "—"}</td>
      <td>${h.Karar ?? "—"}</td>
      <td>${h.Trend ?? "—"}</td>
      <td>${h.Momentum ?? "—"}</td>
      <td>${h.RSI ?? "—"}</td>
      <td>${h.ADX ?? "—"}</td>
      <td>${h.ATR ?? "—"}</td>
      <td>${h.Teknik ?? "—"}</td>
      <td>${h.Temel ?? "—"}</td>
      <td>${h.Risk ?? "—"}</td>
      <td>${paraFormat(h.Destek)}</td>
      <td>${paraFormat(h.Direnc)}</td>
      <td>${paraFormat(h.Stop)}</td>
      <td>${paraFormat(h.Hedef)}</td>
      <td>${h["Risk/Odul"] ?? "—"}</td>
    </tr>`
    )
    .join("");
}

function filtreTablosunuDoldur(hisseler) {
  const gövde = document.querySelector("#filtre-tablo tbody");

  if (!hisseler.length) {
    gövde.innerHTML = '<tr><td colspan="10" class="bos-satir">Henüz tarama verisi yok.</td></tr>';
    return;
  }

  // Süzgeçten geçenler üstte olacak şekilde sırala
  const sirali = [...hisseler].sort((a, b) => (b.FiltreGecti === true) - (a.FiltreGecti === true));

  gövde.innerHTML = sirali
    .map((h) => {
      const gecti = h.FiltreGecti === true;
      const durum = gecti
        ? '<span class="rozet rozet-gecti">✓ Güçlü Dizilim</span>'
        : '<span class="rozet rozet-bekliyor">—</span>';

      return `
    <tr class="${gecti ? "satir-gecti" : ""}">
      <td>${h.Hisse}</td>
      <td>${paraFormat(h.Fiyat)}</td>
      <td>${paraFormat(h.EMA9)}</td>
      <td>${paraFormat(h.EMA21)}</td>
      <td>${paraFormat(h.SMA50)}</td>
      <td>${paraFormat(h.SMA200)}</td>
      <td>${h.ADX ?? "—"}</td>
      <td>${h.MACD ?? "—"}</td>
      <td>${h.RSI ?? "—"}</td>
      <td>${durum}</td>
    </tr>`;
    })
    .join("");
}

function portfoyOzetiDoldur(portfoy, hisseler) {
  const fiyatMap = Object.fromEntries(hisseler.map((h) => [h.Hisse, h.Fiyat]));

  let pozisyonDegeri = 0;
  for (const [hisse, poz] of Object.entries(portfoy.pozisyonlar || {})) {
    const guncelFiyat = fiyatMap[hisse] ?? poz.maliyet;
    pozisyonDegeri += guncelFiyat * poz.adet;
  }

  const toplamDeger = portfoy.nakit + pozisyonDegeri;
  const kz = toplamDeger - (portfoy.baslangic_sermaye ?? toplamDeger);
  const baslangic = portfoy.baslangic_sermaye || toplamDeger || 1;
  const kzYuzde = (kz / baslangic) * 100;

  document.getElementById("ozet-nakit").textContent = paraFormat(portfoy.nakit);
  document.getElementById("ozet-pozisyon").textContent = paraFormat(pozisyonDegeri);
  document.getElementById("ozet-toplam").textContent = paraFormat(toplamDeger);

  const kzEl = document.getElementById("ozet-kz");
  kzEl.textContent = (kz >= 0 ? "+" : "") + paraFormat(kz);
  kzEl.className = "ozet-deger " + kzSinifi(kz);

  const kzYuzdeEl = document.getElementById("ozet-kz-yuzde");
  kzYuzdeEl.textContent = (kzYuzde >= 0 ? "+" : "") + kzYuzde.toFixed(2) + "%";
  kzYuzdeEl.className = "ozet-yuzde " + kzSinifi(kz);
}

function pozisyonTablosunuDoldur(portfoy, hisseler) {
  const gövde = document.querySelector("#pozisyon-tablo tbody");
  const fiyatMap = Object.fromEntries(hisseler.map((h) => [h.Hisse, h.Fiyat]));
  const pozisyonlar = Object.entries(portfoy.pozisyonlar || {});

  if (!pozisyonlar.length) {
    gövde.innerHTML = '<tr><td colspan="8" class="bos-satir">Şu anda açık pozisyon yok.</td></tr>';
    return;
  }

  gövde.innerHTML = pozisyonlar
    .map(([hisse, poz]) => {
      const guncelFiyat = fiyatMap[hisse] ?? poz.maliyet;
      const deger = guncelFiyat * poz.adet;
      const kz = (guncelFiyat - poz.maliyet) * poz.adet;

      return `
      <tr>
        <td>${hisse}</td>
        <td>${poz.adet}</td>
        <td>${paraFormat(poz.maliyet)}</td>
        <td>${paraFormat(guncelFiyat)}</td>
        <td>${paraFormat(deger)}</td>
        <td class="${kzSinifi(kz)}">${(kz >= 0 ? "+" : "") + paraFormat(kz)}</td>
        <td>${paraFormat(poz.stop_takip)}</td>
        <td>${paraFormat(poz.hedef_takip)}</td>
      </tr>`;
    })
    .join("");
}

function islemTablosunuDoldur(islemler) {
  const gövde = document.querySelector("#islem-tablo tbody");

  if (!islemler.length) {
    gövde.innerHTML = '<tr><td colspan="7" class="bos-satir">Henüz işlem yapılmadı.</td></tr>';
    return;
  }

  const sonIslemler = [...islemler].reverse().slice(0, 50);

  gövde.innerHTML = sonIslemler
    .map(
      (i) => `
    <tr class="${i.tip === 'AL' ? 'satir-al' : 'satir-sat'}">
      <td>${new Date(i.tarih).toLocaleString("tr-TR")}</td>
      <td>${i.hisse}</td>
      <td>${i.tip}</td>
      <td>${i.adet}</td>
      <td>${paraFormat(i.fiyat)}</td>
      <td>${paraFormat(i.tutar)}</td>
      <td>${i.gerekce ?? ""}</td>
    </tr>`
    )
    .join("");
}

// ----------------------------------------------------------
// GitHub Actions'ı tetikleme
// ----------------------------------------------------------

const taramaButon = document.getElementById("tarama-buton");

async function taramaBaslat() {

  let token = tokenGetir();

  if (!token) {
    token = await tokenIste();
    if (!token) return; // kullanıcı iptal etti
  }

  taramaButon.disabled = true;
  taramaButon.textContent = "Başlatılıyor…";

  try {
    const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${GITHUB_WORKFLOW_FILE}/dispatches`;

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: GITHUB_BRANCH }),
    });

    if (res.status === 204) {
      taramaButon.textContent = "Çalışıyor… (1-3 dk)";
      taramaSonucunuBekle();
    } else if (res.status === 401 || res.status === 403) {
      localStorage.removeItem(TOKEN_ANAHTARI);
      taramaButon.disabled = false;
      taramaButon.textContent = "▶ Yeni Tarama Başlat";
      const yeniToken = await tokenIste();
      if (yeniToken) {
        taramaBaslat(); // doğru token ile tekrar dene
      }
    } else {
      let mesaj = res.status;
      try {
        const hata = await res.json();
        mesaj = hata.message || mesaj;
      } catch (_) {}
      alert("Tarama başlatılamadı (" + mesaj + ").");
      taramaButon.disabled = false;
      taramaButon.textContent = "▶ Yeni Tarama Başlat";
    }
  } catch (err) {
    alert("Bağlantı hatası: " + err.message);
    taramaButon.disabled = false;
    taramaButon.textContent = "▶ Yeni Tarama Başlat";
  }
}

function taramaSonucunuBekle() {

  const baslangicZamani = sonGuncellemeZamani;
  const baslangic = Date.now();
  const MAX_BEKLEME_MS = 6 * 60 * 1000; // 6 dakika sonra pes et
  const ARALIK_MS = 15 * 1000;          // 15 saniyede bir kontrol et

  if (bekleyenInterval) clearInterval(bekleyenInterval);

  bekleyenInterval = setInterval(async () => {

    if (Date.now() - baslangic > MAX_BEKLEME_MS) {
      clearInterval(bekleyenInterval);
      taramaButon.disabled = false;
      taramaButon.textContent = "▶ Yeni Tarama Başlat";
      alert("Tarama beklenenden uzun sürdü. GitHub'ın Actions sekmesinden durumu kontrol edebilirsin.");
      return;
    }

    try {
      const res = await fetch("data/sonuc.json?_=" + Date.now());
      if (!res.ok) return;
      const data = await res.json();

      if (data.guncelleme && data.guncelleme !== baslangicZamani) {
        clearInterval(bekleyenInterval);
        taramaButon.disabled = false;
        taramaButon.textContent = "▶ Yeni Tarama Başlat";
        veriYukle();
      }
    } catch (err) {
      // sessizce tekrar dener
    }

  }, ARALIK_MS);
}

// ----------------------------------------------------------
// Manuel Portföy — repoda docs/data/manuel-portfoy.json olarak
// saklanır (botunki gibi). Okuma herkese açık (statik dosya),
// yazma GitHub API üzerinden aynı token ile yapılır — token'ın
// artık "Contents: Read and write" yetkisi de olması gerekiyor.
// Bu sayede hangi cihaz/tarayıcıdan girersen gir aynı veriyi
// görürsün.
// ----------------------------------------------------------

const MANUEL_DOSYA_YOLU = "docs/data/manuel-portfoy.json";
const MANUEL_BASLANGIC_SERMAYE = 100000;

let sonBilinenFiyatlar = {};
let manuelVeri = null;   // en son bilinen içerik (önbellek)
let manuelSha = null;    // GitHub'daki dosyanın son bilinen sürüm kimliği

function yuvarla(x) {
  return Math.round(x * 100) / 100;
}

function utf8ToBase64(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

function varsayilanManuelVeri() {
  return {
    nakit: MANUEL_BASLANGIC_SERMAYE,
    baslangic_sermaye: MANUEL_BASLANGIC_SERMAYE,
    pozisyonlar: {},
    islemler: [],
  };
}

async function manuelYukle(zorlaYenile) {
  if (manuelVeri && !zorlaYenile) return manuelVeri;

  try {
    const res = await fetch("data/manuel-portfoy.json?_=" + Date.now());
    manuelVeri = res.ok ? await res.json() : varsayilanManuelVeri();
  } catch (err) {
    manuelVeri = varsayilanManuelVeri();
  }

  return manuelVeri;
}

async function manuelShaGetir(token) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${MANUEL_DOSYA_YOLU}?ref=${GITHUB_BRANCH}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json" },
  });
  if (res.status === 404) return null; // dosya repoda henüz yok
  if (!res.ok) throw new Error("Dosya bilgisi alınamadı (HTTP " + res.status + ")");
  const veri = await res.json();
  return veri.sha;
}

// data'yı GitHub'a commit eder. sha çakışmasında (409) bir kere tekrar dener.
async function manuelKaydetUzaktan(data) {

  let token = tokenGetir();
  if (!token) {
    token = await tokenIste();
    if (!token) throw new Error("Token girilmedi, kaydedilemedi.");
  }

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${MANUEL_DOSYA_YOLU}`;
  const icerik = utf8ToBase64(JSON.stringify(data, null, 2));

  async function gonder(sha) {
    return fetch(url, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Manuel portföy güncellendi",
        content: icerik,
        sha: sha || undefined,
        branch: GITHUB_BRANCH,
      }),
    });
  }

  if (!manuelSha) {
    manuelSha = await manuelShaGetir(token);
  }

  let res = await gonder(manuelSha);

  if (res.status === 409) {
    // başka bir cihaz/sekme aynı anda yazmış olabilir - sha'yı tazeleyip tekrar dene
    manuelSha = await manuelShaGetir(token);
    res = await gonder(manuelSha);
  }

  if (res.status === 401 || res.status === 403) {
    localStorage.removeItem(TOKEN_ANAHTARI);
    throw new Error(
      "Token geçersiz/yetkisiz. Token'ın hem \"Actions: Read and write\" hem de " +
      "\"Contents: Read and write\" yetkisi olmalı."
    );
  }

  if (!res.ok) {
    const hata = await res.json().catch(() => ({}));
    throw new Error(hata.message || "HTTP " + res.status);
  }

  const sonuc = await res.json();
  manuelSha = sonuc.content.sha;
  manuelVeri = data;
}

async function manuelGoster() {
  const data = await manuelYukle();
  const fiyatMap = sonBilinenFiyatlar;

  let pozisyonDegeri = 0;
  for (const [hisse, poz] of Object.entries(data.pozisyonlar)) {
    const guncelFiyat = fiyatMap[hisse] ?? poz.maliyet;
    pozisyonDegeri += guncelFiyat * poz.adet;
  }

  const toplamDeger = data.nakit + pozisyonDegeri;
  const kz = toplamDeger - data.baslangic_sermaye;
  const kzYuzde = (kz / data.baslangic_sermaye) * 100;

  document.getElementById("manuel-nakit").textContent = paraFormat(data.nakit);
  document.getElementById("manuel-pozisyon").textContent = paraFormat(pozisyonDegeri);
  document.getElementById("manuel-toplam").textContent = paraFormat(toplamDeger);

  const kzEl = document.getElementById("manuel-kz");
  kzEl.textContent = (kz >= 0 ? "+" : "") + paraFormat(kz);
  kzEl.className = "ozet-deger " + kzSinifi(kz);

  const kzYuzdeEl = document.getElementById("manuel-kz-yuzde");
  kzYuzdeEl.textContent = (kzYuzde >= 0 ? "+" : "") + kzYuzde.toFixed(2) + "%";
  kzYuzdeEl.className = "ozet-yuzde " + kzSinifi(kz);

  // ---- Pozisyon tablosu ----
  const povucu = document.querySelector("#manuel-pozisyon-tablo tbody");
  const pozGirisleri = Object.entries(data.pozisyonlar);

  if (!pozGirisleri.length) {
    povucu.innerHTML = '<tr><td colspan="7" class="bos-satir">Henüz pozisyon eklemedin.</td></tr>';
  } else {
    povucu.innerHTML = pozGirisleri
      .map(([hisse, poz]) => {
        const guncelFiyat = fiyatMap[hisse] ?? poz.maliyet;
        const deger = guncelFiyat * poz.adet;
        const kzPoz = (guncelFiyat - poz.maliyet) * poz.adet;

        return `
      <tr>
        <td>${hisse}</td>
        <td>${poz.adet}</td>
        <td>${paraFormat(poz.maliyet)}</td>
        <td>${paraFormat(guncelFiyat)}</td>
        <td>${paraFormat(deger)}</td>
        <td class="${kzSinifi(kzPoz)}">${(kzPoz >= 0 ? "+" : "") + paraFormat(kzPoz)}</td>
        <td><button class="mini-buton" onclick="manuelSat('${hisse}')">Sat</button></td>
      </tr>`;
      })
      .join("");
  }

  // ---- İşlem geçmişi ----
  const igovde = document.querySelector("#manuel-islem-tablo tbody");

  if (!data.islemler.length) {
    igovde.innerHTML = '<tr><td colspan="6" class="bos-satir">Henüz işlem yok.</td></tr>';
  } else {
    const sonIslemler = [...data.islemler].reverse().slice(0, 50);
    igovde.innerHTML = sonIslemler
      .map(
        (i) => `
      <tr class="${i.tip === "AL" ? "satir-al" : "satir-sat"}">
        <td>${new Date(i.tarih).toLocaleString("tr-TR")}</td>
        <td>${i.hisse}</td>
        <td>${i.tip}</td>
        <td>${i.adet}</td>
        <td>${paraFormat(i.fiyat)}</td>
        <td>${paraFormat(i.tutar)}</td>
      </tr>`
      )
      .join("");
  }
}

const manuelAlButon = document.getElementById("manuel-al-buton");

async function manuelAl() {
  const hisseInput = document.getElementById("manuel-hisse");
  const adetInput = document.getElementById("manuel-adet");
  const fiyatInput = document.getElementById("manuel-fiyat");

  const hisse = hisseInput.value.trim().toUpperCase();
  const adet = parseInt(adetInput.value, 10);
  const fiyat = parseFloat(fiyatInput.value);

  if (!hisse) { alert("Hisse kodu gir (örn. ASELS)."); return; }
  if (!adet || adet <= 0) { alert("Geçerli bir adet gir."); return; }
  if (!fiyat || fiyat <= 0) { alert("Geçerli bir fiyat gir."); return; }

  const data = await manuelYukle(true); // yazmadan önce en güncelini al

  const tutar = yuvarla(adet * fiyat);

  if (tutar > data.nakit) {
    alert(`Yetersiz nakit. Elindeki: ${paraFormat(data.nakit)}, gereken: ${paraFormat(tutar)}`);
    return;
  }

  const mevcut = data.pozisyonlar[hisse];
  if (mevcut) {
    const toplamAdet = mevcut.adet + adet;
    const toplamMaliyet = mevcut.adet * mevcut.maliyet + adet * fiyat;
    data.pozisyonlar[hisse] = { adet: toplamAdet, maliyet: yuvarla(toplamMaliyet / toplamAdet) };
  } else {
    data.pozisyonlar[hisse] = { adet, maliyet: fiyat };
  }

  data.nakit = yuvarla(data.nakit - tutar);
  data.islemler.push({ tarih: new Date().toISOString(), hisse, tip: "AL", adet, fiyat, tutar });

  manuelAlButon.disabled = true;
  manuelAlButon.textContent = "Kaydediliyor…";

  try {
    await manuelKaydetUzaktan(data);
    hisseInput.value = "";
    adetInput.value = "";
    fiyatInput.value = "";
    await manuelGoster();
  } catch (err) {
    alert("Kaydedilemedi: " + err.message);
  } finally {
    manuelAlButon.disabled = false;
    manuelAlButon.textContent = "Satın Al";
  }
}

async function manuelSat(hisse) {
  const data = await manuelYukle(true);
  const poz = data.pozisyonlar[hisse];
  if (!poz) return;

  const fiyat = sonBilinenFiyatlar[hisse] ?? poz.maliyet;
  const tutar = yuvarla(fiyat * poz.adet);

  data.nakit = yuvarla(data.nakit + tutar);
  data.islemler.push({ tarih: new Date().toISOString(), hisse, tip: "SAT", adet: poz.adet, fiyat, tutar });
  delete data.pozisyonlar[hisse];

  try {
    await manuelKaydetUzaktan(data);
    await manuelGoster();
  } catch (err) {
    alert("Kaydedilemedi: " + err.message);
  }
}

manuelAlButon.addEventListener("click", manuelAl);

document.getElementById("manuel-sifirla-buton").addEventListener("click", async () => {
  if (!confirm("Manuel portföyü tamamen sıfırlamak istediğine emin misin? Bu geri alınamaz.")) return;
  try {
    await manuelKaydetUzaktan(varsayilanManuelVeri());
    await manuelGoster();
  } catch (err) {
    alert("Sıfırlanamadı: " + err.message);
  }
});
