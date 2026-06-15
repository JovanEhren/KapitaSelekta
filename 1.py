import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import Counter
from transformers import pipeline
import matplotlib.pyplot as plt

# =========================
# 1. SCRAPING ARTIKEL
# =========================

url = "https://www.kompas.id/artikel/rupiah-tembus-rp-18000-siap-siap-harga-barang-dan-jasa-makin-mahal"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

# Judul
title = soup.find("h1").get_text(strip=True)

# Isi artikel
paragraphs = soup.find_all("p")

article_text = " ".join([
    p.get_text(" ", strip=True)
    for p in paragraphs
])

print("Judul Artikel:")
print(title)

# =========================
# 2. PREPROCESSING
# =========================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

clean_article = clean_text(article_text)

# =========================
# 3. SIMPAN DATASET ARTIKEL
# =========================

df_article = pd.DataFrame({
    "judul": [title],
    "isi_artikel": [clean_article]
})

df_article.to_csv(
    "artikel_berita.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 4. PECAH MENJADI KALIMAT
# =========================

sentences = re.split(r'[.!?]', article_text)

sentences = [
    clean_text(s)
    for s in sentences
    if len(s.strip()) > 20
]

df_sentences = pd.DataFrame(
    sentences,
    columns=["kalimat"]
)

# =========================
# 5. SENTIMENT ANALYSIS
# =========================

classifier = pipeline(
    "sentiment-analysis",
    model="w11wo/indonesian-roberta-base-sentiment-classifier"
)

df_sentences["sentiment"] = df_sentences["kalimat"].apply(
    lambda x: classifier(x[:512])[0]["label"]
)

print(df_sentences.head())

# Simpan hasil
df_sentences.to_csv(
    "artikel_sentiment.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 6. VISUALISASI SENTIMEN
# =========================

sentiment_counts = df_sentences["sentiment"].value_counts()

plt.figure(figsize=(6,4))
sentiment_counts.plot(kind="bar")
plt.title("Sentiment Artikel Berita")
plt.xlabel("Sentimen")
plt.ylabel("Jumlah Kalimat")
plt.tight_layout()
plt.show()

# =========================
# 7. ANALISIS KEYWORD
# =========================

stopwords = {
    "dan","yang","di","ke","dari","ini","itu",
    "untuk","dengan","pada","adalah","sebagai",
    "karena","juga","oleh","atau","dalam",
    "akan","telah","lebih","hingga","para"
}

words = clean_article.split()

filtered_words = [
    word for word in words
    if word not in stopwords
    and len(word) > 3
]

top_keywords = Counter(filtered_words).most_common(15)

keyword_df = pd.DataFrame(
    top_keywords,
    columns=["keyword","jumlah"]
)

print("\nTop Keywords:")
print(keyword_df)

# Simpan keyword
keyword_df.to_csv(
    "keyword_artikel.csv",
    index=False,
    encoding="utf-8-sig"
)

# =========================
# 8. VISUALISASI KEYWORD
# =========================

plt.figure(figsize=(10,5))

plt.bar(
    keyword_df["keyword"],
    keyword_df["jumlah"]
)

plt.xticks(rotation=45)
plt.title("Top 15 Keyword Artikel")
plt.tight_layout()
plt.show()