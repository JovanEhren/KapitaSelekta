import os
import re
import csv
import time
import torch
import matplotlib.pyplot as plt
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# ── KONFIGURASI ──────────────────────────────────────────────────────────────
USERNAME      = 'ojasajo0456'
PASSWORD      = 'okinyby2525'
POST_URL      = 'https://www.instagram.com/p/DYWkER8kWRY/'
OUT_COMMENTS  = 'comments.csv'
OUT_SENTIMENT = 'sentiment_results.csv'
OUT_PIE       = 'sentiment_pie.png'
OUT_BAR       = 'sentiment_bar.png'
MODEL_NAME    = 'mdhugol/indonesia-bert-sentiment-classification'
LABEL_MAP     = {'LABEL_0': 'Positif', 'LABEL_1': 'Netral', 'LABEL_2': 'Negatif'}
COLOR_MAP     = {'Positif': '#4CAF50', 'Netral': '#2196F3', 'Negatif': '#F44336'}
MAX_TOKEN_LEN = 512
# ─────────────────────────────────────────────────────────────────────────────

# ── FILTER NOISE ─────────────────────────────────────────────────────────────
# Semua frasa UI Instagram yang pasti bukan komentar
UI_BLACKLIST = {
    'instagram', 'home', 'reels', 'messages', 'search', 'explore',
    'notifications', 'create', 'profile', 'more', 'threads', 'meta',
    'follow', 'following', 'unfollow', 'like', 'comment', 'share',
    'save', 'sponsored', 'settings', 'verified', 'report', 'block',
    'mute', 'reel', 'igtv', 'highlights',
    # Frasa 2+ kata
    'home home', 'reels reels', 'messages messages', 'search search',
    'notifications notifications', 'explore explore', 'profile profile',
    'new post', 'new post create', 'settings more', 'threads threads',
    'also from meta', 'also from meta also from meta',
    'log in', 'sign up', 'log in sign up', 'sign up log in',
    'switch accounts', 'add account', 'not now',
    'see all', 'see more', 'see less', 'see translation',
    'load more comments', 'view more comments',
    'view replies', 'hide replies', 'view all replies',
    'suggested for you', 'suggested accounts',
    'turn on notifications', 'about this account',
}

NOISE_RE = [
    re.compile(r'^\d+\s*(likes?|comments?|views?|followers?|following)$', re.I),
    re.compile(r'^view\s+all\s+\d+\s+repl', re.I),       # "View all 4 replies"
    re.compile(r'^load\s+more', re.I),
    re.compile(r'^\d+[wdhms]\s*ago$', re.I),              # "2d ago"
    re.compile(r'^\d+$'),                                  # angka murni
    re.compile(r'^@[\w.]+$'),                              # @mention saja
    re.compile(r'^[\w._]+$'),                              # satu token (username)
    re.compile(r'^#[\w]+$'),                               # hashtag saja
    re.compile(r'^(reply|replied|replying)$', re.I),
    re.compile(r'^(\w+)\s+\1$', re.I),                    # "Kata Kata" duplikasi
    re.compile(r'^also\s+from\s+meta', re.I),
    re.compile(r'^see\s+translation$', re.I),
    re.compile(r'^verified(\s+\w+){0,3}$', re.I),         # "Verified 4w" dll
    re.compile(r'^[\w._]+\s+verified\b', re.I),           # "username Verified ..."
    re.compile(r'^[\w._]+\s+\d+[wdhms]$', re.I),         # "username 4w"
]

def is_noise(text):
    t = text.strip()
    # Terlalu pendek
    if len(t) < 10:
        return True
    # Cocok blacklist (case-insensitive)
    if t.lower() in UI_BLACKLIST:
        return True
    # Cocok pola regex
    for pat in NOISE_RE:
        if pat.match(t):
            return True
    # Kurang dari 3 kata → kemungkinan besar bukan komentar
    if len(t.split()) < 3:
        return True
    return False
# ─────────────────────────────────────────────────────────────────────────────


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    )
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
    )
    return driver


def dismiss_cookie_popup(driver):
    for xpath in [
        "//button[contains(text(),'Allow')]",
        "//button[contains(text(),'Accept')]",
        "//button[contains(text(),'Terima')]",
        "//button[contains(text(),'Izinkan')]",
        "//button[contains(text(),'Only allow essential cookies')]",
    ]:
        try:
            btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            btn.click()
            print("      [popup] Cookie consent ditutup.")
            time.sleep(1)
            return
        except Exception:
            pass


def login(driver, username, password):
    print("[1/4] Login ke Instagram...")
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(3)
    dismiss_cookie_popup(driver)
    driver.save_screenshot('debug_login.png')
    print(f"      URL: {driver.current_url}")

    username_field = None
    for attempt, (by, val) in enumerate([
        (By.NAME, 'username'),
        (By.NAME, 'email'),
        (By.CSS_SELECTOR, 'input[type="text"]'),
        (By.XPATH, '//input[@autocomplete="username"]'),
    ]):
        try:
            username_field = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((by, val)))
            print(f"      Field username ditemukan (selector #{attempt+1}).")
            break
        except Exception:
            continue

    if username_field is None:
        print("❌ Form login tidak ditemukan. Cek debug_login.png")
        input("   Login manual di browser lalu tekan Enter: ")
        return

    username_field.click()
    username_field.clear()
    username_field.send_keys(username)
    time.sleep(0.5)

    password_field = None
    for by, val in [
        (By.NAME, 'password'),
        (By.CSS_SELECTOR, 'input[type="password"]'),
        (By.XPATH, '//input[@autocomplete="current-password"]'),
    ]:
        try:
            password_field = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((by, val)))
            break
        except Exception:
            continue

    if password_field is None:
        print("❌ Field password tidak ditemukan.")
        input("   Login manual lalu tekan Enter: ")
        return

    password_field.click()
    password_field.clear()
    password_field.send_keys(password)
    time.sleep(0.5)
    password_field.send_keys(Keys.RETURN)

    try:
        WebDriverWait(driver, 20).until(lambda d: '/accounts/login/' not in d.current_url)
        print(f"      Login selesai. URL: {driver.current_url}")
    except Exception:
        driver.save_screenshot('debug_after_login.png')
        print("      ⚠️  Cek debug_after_login.png — mungkin ada 2FA/CAPTCHA.")
        input("         Selesaikan di browser lalu tekan Enter: ")


def scrape_comments(driver, post_url):
    print("[2/4] Membuka post dan scroll komentar...")
    driver.get(post_url)
    time.sleep(4)
    driver.save_screenshot('debug_post.png')

    try:
        scroll_div = driver.find_element(By.CSS_SELECTOR, 'div.x5yr21d.xw2csxc.x1odjw0f.x1n2onr6')
        last_h = driver.execute_script("return arguments[0].scrollHeight", scroll_div)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)
            time.sleep(2)
            new_h = driver.execute_script("return arguments[0].scrollHeight", scroll_div)
            if new_h == last_h:
                break
            last_h = new_h
    except Exception:
        last_h = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    comments, seen = [], set()

    for span in soup.find_all('span'):
        # Skip elemen navigasi / tombol
        parent = span.parent
        if parent and parent.name in ['a', 'button', 'nav']:
            continue
        if span.get('aria-hidden') == 'true':
            continue

        text = span.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()

        if text in seen or is_noise(text):
            continue

        seen.add(text)
        comments.append(text)

    print(f"      Ditemukan {len(comments)} komentar valid (setelah filter noise).")
    return comments


def save_comments_csv(comments, filepath):
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['no', 'komentar'])
        for i, c in enumerate(comments, 1):
            writer.writerow([i, c])


# ── SENTIMENT ────────────────────────────────────────────────────────────────

def load_model(model_name):
    print(f"\n[3/4] Memuat model IndoBERT: {model_name}")
    print("      (Download otomatis ~500MB jika belum pernah dipakai)")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    device = 0 if torch.cuda.is_available() else -1
    print(f"      Model siap. Menggunakan: {'GPU' if device == 0 else 'CPU'}")
    classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer, device=device)
    return classifier, tokenizer


def truncate_text(text, tokenizer, max_len=MAX_TOKEN_LEN):
    tokens = tokenizer.encode(text, add_special_tokens=True)
    if len(tokens) > max_len:
        tokens = tokens[:max_len - 1] + [tokenizer.sep_token_id]
        text = tokenizer.decode(tokens, skip_special_tokens=True)
    return text


def analyze_sentiment(comments, classifier, tokenizer, label_map):
    print(f"[4/4] Analisis sentimen {len(comments)} komentar...")
    results = []
    for i, comment in enumerate(comments, 1):
        if i % 50 == 0 or i == len(comments):
            print(f"      Progress: {i}/{len(comments)}")
        try:
            text = truncate_text(comment, tokenizer)
            pred = classifier(text)[0]
            label = label_map.get(pred['label'], pred['label'])
            score = round(pred['score'], 4)
        except Exception:
            label = 'Error'
            score = 0.0
        results.append({'komentar': comment, 'sentimen': label, 'confidence': score})
    return results


def save_sentiment_csv(results, filepath):
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['no', 'komentar', 'sentimen', 'confidence'])
        writer.writeheader()
        for i, row in enumerate(results, 1):
            writer.writerow({'no': i, **row})
    print(f"      Hasil sentimen disimpan: {filepath}")


# ── VISUALISASI ──────────────────────────────────────────────────────────────

def make_charts(results, color_map, pie_path, bar_path):
    labels_all = [r['sentimen'] for r in results if r['sentimen'] != 'Error']
    counts = Counter(labels_all)
    total = sum(counts.values())

    sentimen_order = ['Positif', 'Netral', 'Negatif']
    labels = [s for s in sentimen_order if s in counts]
    values = [counts[s] for s in labels]
    colors = [color_map[s] for s in labels]

    # Pie Chart
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors,
        autopct=lambda p: f'{p:.1f}%\n({int(round(p * total / 100))})',
        startangle=140,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        textprops={'fontsize': 12},
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight('bold')
    ax.set_title('Distribusi Sentimen Komentar Instagram', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(pie_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"      Pie chart disimpan: {pie_path}")
    plt.close()

    # Bar Chart
    avg_conf = {}
    for s in labels:
        confs = [r['confidence'] for r in results if r['sentimen'] == s]
        avg_conf[s] = round(sum(confs) / len(confs) * 100, 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    bars = axes[0].bar(labels, values, color=colors, edgecolor='white', width=0.5)
    for bar, val in zip(bars, values):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     str(val), ha='center', fontsize=12, fontweight='bold')
    axes[0].set_title('Jumlah Komentar per Sentimen', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Jumlah Komentar')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)
    axes[0].set_ylim(0, max(values) * 1.15)

    bars2 = axes[1].bar(labels, [avg_conf[s] for s in labels], color=colors, edgecolor='white', width=0.5)
    for bar, s in zip(bars2, labels):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     f'{avg_conf[s]}%', ha='center', fontsize=12, fontweight='bold')
    axes[1].set_title('Rata-rata Confidence Model (%)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Confidence (%)')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)
    axes[1].set_ylim(0, 110)

    plt.suptitle('Analisis Sentimen Komentar Instagram — IndoBERT', fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(bar_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"      Bar chart disimpan: {bar_path}")
    plt.close()

    print("\n── RINGKASAN SENTIMEN ─────────────────────────")
    for s in labels:
        pct = counts[s] / total * 100
        print(f"   {s:<10} : {counts[s]:>4} komentar ({pct:.1f}%) | avg confidence {avg_conf[s]}%")
    print(f"   {'Total':<10} : {total:>4} komentar")
    print("───────────────────────────────────────────────")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    driver = init_driver()
    try:
        login(driver, USERNAME, PASSWORD)
        comments = scrape_comments(driver, POST_URL)
        save_comments_csv(comments, OUT_COMMENTS)
        print(f"      Komentar mentah disimpan: {OUT_COMMENTS}")
    finally:
        driver.quit()

    classifier, tokenizer = load_model(MODEL_NAME)
    results = analyze_sentiment(comments, classifier, tokenizer, LABEL_MAP)
    save_sentiment_csv(results, OUT_SENTIMENT)
    make_charts(results, COLOR_MAP, OUT_PIE, OUT_BAR)

    print("\n✅ Selesai! File yang dihasilkan:")
    print(f"   • {OUT_COMMENTS:<25} → komentar mentah")
    print(f"   • {OUT_SENTIMENT:<25} → hasil sentimen per komentar")
    print(f"   • {OUT_PIE:<25} → pie chart distribusi sentimen")
    print(f"   • {OUT_BAR:<25} → bar chart jumlah & confidence")


if __name__ == '__main__':
    main()