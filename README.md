# 📰 Script 1: Scraping Artikel Berita + Analisis Sentimen

Skrip ini mengambil artikel berita dari Kompas.id tentang **Rupiah tembus Rp18.000**, melakukan preprocessing teks, analisis sentimen menggunakan model IndoBERT/RoBERTa Bahasa Indonesia, serta mengekstrak keyword utama dari artikel.

---

## 📁 Output yang Dihasilkan

| File | Deskripsi |
|------|-----------|
| `artikel_berita.csv` | Judul dan isi artikel yang sudah dibersihkan |
| `artikel_sentiment.csv` | Tiap kalimat artikel beserta label sentimennya |
| `keyword_artikel.csv` | Top 15 keyword yang paling sering muncul |

---

## ⚙️ Requirements

Pastikan Python sudah terinstall (versi **3.8+**), lalu install dependensi berikut:

```bash
pip install requests beautifulsoup4 pandas transformers matplotlib torch
```

> **Catatan:** Model `w11wo/indonesian-roberta-base-sentiment-classifier` akan otomatis diunduh dari Hugging Face saat pertama kali dijalankan (~500MB). Pastikan koneksi internet stabil.

---

## 🚀 Cara Menjalankan

### 1. Clone atau download file skrip

```bash
git clone https://github.com/username/nama-repo.git
cd nama-repo
```

### 2. Jalankan skrip

```bash
python script1_artikel.py
```

### 3. Cek output

Setelah selesai, file berikut akan muncul di folder yang sama:
```
artikel_berita.csv
artikel_sentiment.csv
keyword_artikel.csv
```

---

## 🔄 Alur Kerja Skrip

```
URL Artikel Kompas.id
        ↓
  Scraping HTML (requests + BeautifulSoup)
        ↓
  Ekstrak Judul & Isi Artikel
        ↓
  Preprocessing (clean_text)
  - Lowercase
  - Hapus URL & karakter non-huruf
  - Normalisasi spasi
        ↓
  Simpan → artikel_berita.csv
        ↓
  Pecah menjadi kalimat (split by .!?)
        ↓
  Sentiment Analysis per kalimat
  (model: indonesian-roberta-base-sentiment-classifier)
        ↓
  Simpan → artikel_sentiment.csv
        ↓
  Visualisasi distribusi sentimen (bar chart)
        ↓
  Ekstrak Top 15 Keyword (tanpa stopwords)
        ↓
  Simpan → keyword_artikel.csv
        ↓
  Visualisasi keyword (bar chart)
```

---

## 🧠 Model yang Digunakan

| Properti | Detail |
|----------|--------|
| **Model** | `w11wo/indonesian-roberta-base-sentiment-classifier` |
| **Sumber** | [Hugging Face](https://huggingface.co/w11wo/indonesian-roberta-base-sentiment-classifier) |
| **Bahasa** | Bahasa Indonesia |
| **Output label** | `positive`, `neutral`, `negative` |
| **Input max token** | 512 token per kalimat |

---

## ⚠️ Catatan Penting

- **Artikel Kompas.id** sebagian kontennya berada di balik paywall. Skrip mengambil konten yang tersedia secara publik. Jika konten tidak lengkap, pertimbangkan untuk mengganti URL dengan sumber berita lain yang open-access (seperti Detik, Tempo, Cnnindonesia).
- Jika ingin mengganti artikel, cukup ubah variabel `url` di baris awal skrip:
  ```python
  url = "https://url-artikel-baru.com/..."
  ```
- Proses sentimen bisa memakan waktu **2–10 menit** tergantung panjang artikel dan spesifikasi komputer.

---

## 🗂️ Struktur Folder

```
📂 project/
├── script1_artikel.py       ← Skrip utama
├── artikel_berita.csv       ← Output: isi artikel
├── artikel_sentiment.csv    ← Output: sentimen per kalimat
├── keyword_artikel.csv      ← Output: top keyword
└── README_script1.md        ← Dokumentasi ini
```
