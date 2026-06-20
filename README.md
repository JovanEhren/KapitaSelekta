# 📊 KapitaSelekta — Analisis Sentimen Dollar Rp18.000

> **Misi:** Membandingkan narasi media massa dengan opini publik Instagram terkait pelemahan Rupiah tembus Rp18.000 menggunakan NLP berbasis IndoBERT.

---

## 📁 Struktur Repository

```
KapitaSelekta/
├── NewsScraper.py          # Kode 1 — Scraping artikel berita + analisis sentimen
├── instagram_scraper.py    # Kode 2 — Scraping komentar Instagram + keyword
├── sentiment.py            # Kode 3 — Scraping Instagram + analisis sentimen IndoBERT
├── CSV/
│   ├── artikel_berita.csv
│   ├── artikel_sentiment.csv
│   ├── keyword_artikel.csv
│   ├── comments.csv
│   ├── keyword_count.csv
│   └── sentiment_results.csv
├── Chart/
│   ├── keyword_chart.png
│   ├── sentiment_pie.png
│   └── sentiment_bar.png
└── README.md
```

## 🔧 Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/JovanEhren/KapitaSelekta.git
cd KapitaSelekta
```

### 2. Install Dependensi

```bash
pip install selenium beautifulsoup4 requests pandas transformers torch matplotlib
```

> **Catatan:** Untuk GPU support (opsional, mempercepat analisis sentimen):
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu118
> ```

---

## 🚀 Cara Menjalankan

### 📰 Kode 1 — `NewsScraper.py` (Scraping Artikel Berita)

**Fungsi:** Mengambil artikel dari Kompas.id tentang Rupiah Rp18.000, melakukan preprocessing, analisis sentimen per kalimat dengan RoBERTa, dan ekstrak keyword utama.

```bash
python NewsScraper.py
```

**Output yang dihasilkan:**

| File | Isi |
|------|-----|
| `artikel_berita.csv` | Judul + isi artikel lengkap |
| `artikel_sentiment.csv` | Sentimen per kalimat artikel |
| `keyword_artikel.csv` | Top 15 keyword terbanyak |

**Alur proses:**
```
Scraping URL Kompas.id → Preprocessing teks → Analisis sentimen (RoBERTa) → Ekstrak keyword → Simpan CSV + tampilkan chart
```

---

### 📸 Kode 2 — `instagram_scraper.py` (Scraping Komentar + Keyword)

**Fungsi:** Login ke Instagram, scroll dan ambil semua komentar dari postingan terkait Dollar Rp18.000, lalu hitung frekuensi keyword per kategori.

**Sebelum menjalankan**, pastikan konfigurasi di bagian atas file sudah diisi:

```python
USERNAME  = 'username_instagram_anda'
PASSWORD  = 'password_instagram_anda'
POST_URL  = 'https://www.instagram.com/p/DYWkER8kWRY/'
```

```bash
python instagram_scraper.py
```

**Output yang dihasilkan:**

| File | Isi |
|------|-----|
| `comments.csv` | Semua komentar mentah yang berhasil di-scrape |
| `keyword_count.csv` | Frekuensi keyword beserta kategorinya |
| `keyword_chart.png` | Bar chart horizontal Top 20 keyword |

**Kategori keyword yang dianalisis:**

| Kategori | Contoh Keyword |
|----------|---------------|
| 🔵 Kurs & Rupiah | rupiah, dollar, kurs, 18.000 |
| 🟢 Ekonomi | inflasi, resesi, investasi, IHSG |
| 🟣 Pemerintah | prabowo, jokowi, bank indonesia |
| 🟠 Dampak Masyarakat | harga, sembako, PHK, daya beli |
| 🔴 Sentimen | khawatir, panik, buruk, takut |
| 🟤 Isu Sosial | korupsi, pajak, konoha |

> ⚠️ **Catatan:** Jika muncul CAPTCHA atau verifikasi 2FA saat login, selesaikan secara manual di browser yang terbuka, lalu tekan **Enter** di terminal untuk melanjutkan.

---

### 🤖 Kode 3 — `sentiment.py` (Scraping + Analisis Sentimen IndoBERT)

**Fungsi:** Gabungan scraping Instagram dan analisis sentimen penuh menggunakan model **IndoBERT** (`mdhugol/indonesia-bert-sentiment-classification`). Model akan otomatis didownload (~500MB) pada pertama kali dijalankan.

**Sebelum menjalankan**, isi konfigurasi di bagian atas file:

```python
USERNAME  = 'username_instagram_anda'
PASSWORD  = 'password_instagram_anda'
POST_URL  = 'https://www.instagram.com/p/DYWkER8kWRY/'
```

```bash
python sentiment.py
```

**Output yang dihasilkan:**

| File | Isi |
|------|-----|
| `comments.csv` | Komentar valid (sudah difilter noise) |
| `sentiment_results.csv` | Komentar + label sentimen + confidence score |
| `sentiment_pie.png` | Pie chart distribusi Positif/Netral/Negatif |
| `sentiment_bar.png` | Bar chart jumlah komentar & rata-rata confidence |

**Label Sentimen:**

| Label | Arti |
|-------|------|
| ✅ Positif | Komentar bersifat mendukung/optimis |
| ⚪ Netral | Komentar bersifat informatif/deskriptif |
| ❌ Negatif | Komentar bersifat kritik/pesimis/kekhawatiran |

**Alur proses:**
```
Login Instagram → Scroll komentar → Filter noise → Analisis sentimen IndoBERT → Simpan CSV + chart
```

---

## 🔄 Urutan Menjalankan (Workflow Lengkap)

```
1. python NewsScraper.py          ← Analisis narasi media
         ↓
2. python instagram_scraper.py    ← Ambil opini publik + keyword
         ↓
3. python sentiment.py            ← Analisis sentimen opini publik
         ↓
   Bandingkan hasil keduanya → Identifikasi kesenjangan narasi
```

## 👥 Tim

**-Jovan Ehren(231712538)**
**-Jovan Patra Purba (231712612)**

**Repository:** [JovanEhren/KapitaSelekta](https://github.com/JovanEhren/KapitaSelekta)

---

*Proyek ini dibuat untuk keperluan analisis kebijakan publik — membandingkan narasi media massa dengan opini publik di Instagram terkait pelemahan Rupiah Rp18.000.*
