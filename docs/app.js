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
// ⚠️ GÜVENLİK UYARISI: Buraya koyduğun token, siteyi ziyaret eden HERKES
// tarafından görülebilir (tarayıcı "Kaynağı görüntüle" / Ağ sekmesi).
// SADECE bu repo için, SADECE "Actions: Read and write" yetkisiyle
// oluşturulmuş bir "fine-grained personal access token" kullan.
// Asla "Contents" veya "repo" (tüm reponun tam yetkisi) izni olan bir
// token buraya KOYMA. Nasıl oluşturulacağı README.md'de anlatılıyor.
const GITHUB_OWNER ="bykusfinans-byte";       // <-- değiştir
const GITHUB_REPO = "REPO_ADIN";             // <-- değiştir
const GITHUB_WORKFLOW_FILE = "tarama.yml";
const GITHUB_BRANCH = "main";
const GITHUB_TOKEN = "BURAYA_TOKEN_YAPISTIR"; // <-- değiştir, README'ye bak

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

function portfoyOzetiDoldur(portfoy, hisseler) {
  const fiyatMap = Object.fromEntries(hisseler.map((h) => [h.Hisse, h.Fiyat]));

  let pozisyonDegeri = 0;
  for (const [hisse, poz] of Object.entries(portfoy.pozisyonlar || {})) {
    const guncelFiyat = fiyatMap[hisse] ?? poz.maliyet;
    pozisyonDegeri += guncelFiyat * poz.adet;
  }

  const toplamDeger = portfoy.nakit + pozisyonDegeri;
  const kz = toplamDeger - (portfoy.baslangic_sermaye ?? toplamDeger);

  document.getElementById("ozet-nakit").textContent = paraFormat(portfoy.nakit);
  document.getElementById("ozet-pozisyon").textContent = paraFormat(pozisyonDegeri);
  document.getElementById("ozet-toplam").textContent = paraFormat(toplamDeger);

  const kzEl = document.getElementById("ozet-kz");
  kzEl.textContent = (kz >= 0 ? "+" : "") + paraFormat(kz);
  kzEl.className = "ozet-deger " + kzSinifi(kz);
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

  if (!GITHUB_TOKEN || GITHUB_TOKEN.includes("BURAYA") || GITHUB_OWNER.includes("KULLANICI_ADIN")) {
    alert(
      "Önce app.js dosyasının başındaki GITHUB_OWNER, GITHUB_REPO ve GITHUB_TOKEN " +
      "değerlerini doldurman gerekiyor (README.md'de nasıl token oluşturulacağı anlatılıyor)."
    );
    return;
  }

  taramaButon.disabled = true;
  taramaButon.textContent = "Başlatılıyor…";

  try {
    const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${GITHUB_WORKFLOW_FILE}/dispatches`;

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${GITHUB_TOKEN}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: GITHUB_BRANCH }),
    });

    if (res.status === 204) {
      taramaButon.textContent = "Çalışıyor… (1-3 dk)";
      taramaSonucunuBekle();
    } else {
      let mesaj = res.status;
      try {
        const hata = await res.json();
        mesaj = hata.message || mesaj;
      } catch (_) {}
      alert("Tarama başlatılamadı (" + mesaj + "). Token'ın \"Actions: Read and write\" yetkisi olduğundan emin ol.");
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
