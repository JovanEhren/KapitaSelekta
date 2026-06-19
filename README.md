# I. Analisis Sentimen Artikel Berita Menggunakan IndoBERT

## Deskripsi

Proyek ini merupakan implementasi **web scraping**, **preprocessing teks**, **analisis sentimen**, dan **analisis kata kunci** terhadap sebuah artikel berita berbahasa Indonesia. Artikel diambil secara otomatis dari **Kompas.id** dan kemudian diproses menggunakan model **Indonesian RoBERTa** untuk mengetahui sentimen setiap kalimat.

Hasil analisis disimpan dalam bentuk dataset (.csv) serta divisualisasikan menggunakan grafik batang.

---

## Fitur

* Scraping artikel berita dari Kompas.id
* Pembersihan (preprocessing) teks
* Penyimpanan dataset artikel ke file CSV
* Pemisahan artikel menjadi beberapa kalimat
* Analisis sentimen setiap kalimat menggunakan model IndoBERT
* Visualisasi distribusi sentimen
* Analisis kata kunci berdasarkan frekuensi kemunculan
* Visualisasi 15 kata kunci yang paling sering muncul

---

## Teknologi yang Digunakan

* Python 3
* Requests
* BeautifulSoup4
* Pandas
* Regular Expression (re)
* Transformers (Hugging Face)
* Matplotlib

---

## Instalasi

Clone repository:

```bash
git clone https://github.com/username/nama-repository.git
cd nama-repository
```

Install seluruh library yang dibutuhkan:

```bash
pip install requests beautifulsoup4 pandas matplotlib transformers torch
```

---

## Alur Program

```text
Artikel Berita
      │
      ▼
Web Scraping
      │
      ▼
Preprocessing Teks
      │
      ▼
Penyimpanan Dataset
      │
      ▼
Pemisahan Kalimat
      │
      ▼
Analisis Sentimen
      │
      ▼
Visualisasi Sentimen
      │
      ▼
Analisis Kata Kunci
      │
      ▼
Visualisasi Keyword
```

---

## Dataset yang Dihasilkan

Program akan menghasilkan tiga file dataset:

| Nama File               | Deskripsi                                                                   |
| ----------------------- | --------------------------------------------------------------------------- |
| `artikel_berita.csv`    | Berisi judul dan isi artikel yang telah dibersihkan                         |
| `artikel_sentiment.csv` | Berisi setiap kalimat beserta hasil klasifikasi sentimennya                 |
| `keyword_artikel.csv`   | Berisi 15 kata kunci yang paling sering muncul beserta jumlah kemunculannya |

---

## Model Analisis Sentimen

Analisis sentimen dilakukan menggunakan model:

```
w11wo/indonesian-roberta-base-sentiment-classifier
```

Model ini mampu mengklasifikasikan setiap kalimat ke dalam kategori sentimen seperti:

* Positif
* Netral
* Negatif

---

## Hasil Program

Setelah program dijalankan, akan dihasilkan:

1. Dataset artikel (`artikel_berita.csv`)
2. Dataset hasil analisis sentimen (`artikel_sentiment.csv`)
3. Dataset kata kunci (`keyword_artikel.csv`)
4. Grafik distribusi sentimen
5. Grafik 15 kata kunci yang paling sering muncul

---

## Contoh Proses

Input:

* Artikel berita mengenai nilai tukar Rupiah yang mencapai Rp18.000 terhadap Dolar AS.

Output:

* Artikel yang telah dibersihkan.
* Dataset hasil analisis sentimen setiap kalimat.
* Dataset kata kunci.
* Grafik distribusi sentimen.
* Grafik frekuensi kata kunci.

---

## Pengembangan Selanjutnya

Beberapa pengembangan yang dapat dilakukan pada proyek ini antara lain:

* Mendukung scraping banyak artikel sekaligus.
* Menambahkan visualisasi *Word Cloud*.
* Membandingkan sentimen dari beberapa portal berita.
* Menambahkan analisis topik (*Topic Modeling*).
* Menambahkan *Named Entity Recognition* (NER).
* Mengembangkan antarmuka berbasis Streamlit atau Flask agar dapat digunakan secara interaktif.

---

## Lisensi

Proyek ini dibuat untuk keperluan pembelajaran, penelitian, dan pengembangan analisis sentimen terhadap artikel berita berbahasa Indonesia.
