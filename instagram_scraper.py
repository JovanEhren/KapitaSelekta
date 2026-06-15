from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── KONFIGURASI ──────────────────────────────────────────────────────────────
USERNAME     = 'ojasajo0456'
PASSWORD     = 'okinyby2525'
POST_URL     = 'https://www.instagram.com/p/DYWkER8kWRY/'
OUT_COMMENTS = 'comments.csv'
OUT_KEYWORDS = 'keyword_count.csv'
OUT_CHART    = 'keyword_chart.png'
TOP_CHART_N  = 20   # Tampilkan N keyword teratas di chart
# ─────────────────────────────────────────────────────────────────────────────

# Kategori keyword + warna untuk visualisasi
KEYWORD_CATEGORIES = {
    "Kurs & Rupiah": {
        "color": "#2196F3",
        "keywords": ["rupiah", "dollar", "usd", "kurs", "nilai tukar", "18.000", "22.000"],
    },
    "Ekonomi": {
        "color": "#4CAF50",
        "keywords": [
            "ekonomi", "inflasi", "resesi", "krisis", "utang", "investasi",
            "devaluasi", "ekspor", "impor", "cadangan devisa",
            "subsidi", "anggaran", "defisit", "surplus", "neraca",
            "fiskal", "moneter", "suku bunga", "bi rate", "kebijakan",
            "stimulus", "ihsg", "saham", "obligasi", "dolar", "fed",
            "pelemahan", "penguatan", "daya saing",
        ],
    },
    "Pemerintah": {
        "color": "#9C27B0",
        "keywords": [
            "pemerintah", "presiden", "prabowo", "jokowi", "menteri",
            "bank indonesia", "bi", "reformasi",
        ],
    },
    "Dampak Masyarakat": {
        "color": "#FF9800",
        "keywords": [
            "harga", "mahal", "sembako", "bbm", "bensin", "gaji",
            "daya beli", "rakyat", "phk", "pengangguran", "kemiskinan",
            "mbg", "MBG", "makan bergizi gratis",
        ],
    },
    "Sentimen": {
        "color": "#F44336",
        "keywords": [
            "buruk", "khawatir", "panik", "sedih", "takut",
            "setuju", "tidak setuju",
        ],
    },
    "Isu Sosial": {
        "color": "#795548",
        "keywords": ["konoha", "korupsi", "pajak"],
    },
}

# Flatten ke list keyword + mapping keyword → kategori & warna
KEYWORDS = []
KW_COLOR_MAP = {}
KW_CAT_MAP = {}
for cat, val in KEYWORD_CATEGORIES.items():
    for kw in val["keywords"]:
        if kw not in KEYWORDS:
            KEYWORDS.append(kw)
            KW_COLOR_MAP[kw] = val["color"]
            KW_CAT_MAP[kw] = cat


# ── DRIVER ───────────────────────────────────────────────────────────────────

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
    print(f"      URL: {driver.current_url} | Screenshot: debug_login.png")

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
        print("      ⚠️  Mungkin ada 2FA/CAPTCHA. Cek debug_after_login.png")
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
        text = span.get_text(strip=True)
        if len(text) > 3 and text not in seen:
            seen.add(text)
            comments.append(text)

    print(f"      Ditemukan {len(comments)} teks unik.")
    return comments


def save_comments_csv(comments, filepath):
    print(f"[3/4] Menyimpan komentar ke {filepath}...")
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['no', 'komentar'])
        for i, c in enumerate(comments, 1):
            writer.writerow([i, c])
    print(f"      Tersimpan {len(comments)} baris.")


def count_and_save_keywords(comments, keywords, kw_cat_map, filepath):
    print(f"[4/4] Menghitung keyword dan menyimpan ke {filepath}...")
    all_text = ' '.join(comments).lower()
    counts = {kw: all_text.count(kw.lower()) for kw in keywords}
    sorted_counts = dict(
        sorted({k: v for k, v in counts.items() if v > 0}.items(),
               key=lambda x: x[1], reverse=True)
    )
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'keyword', 'kategori', 'jumlah'])
        for rank, (kw, count) in enumerate(sorted_counts.items(), 1):
            writer.writerow([rank, kw, kw_cat_map.get(kw, '-'), count])
    print(f"      {len(sorted_counts)} keyword muncul dari {len(keywords)} total.")
    return sorted_counts


def make_chart(sorted_counts, kw_color_map, kw_cat_map, top_n, filepath):
    if not sorted_counts:
        print("      Tidak ada keyword yang muncul — chart dilewati.")
        return

    # Ambil top N
    items = list(sorted_counts.items())[:top_n]
    labels = [kw for kw, _ in items]
    values = [v for _, v in items]
    colors = [kw_color_map.get(kw, '#607D8B') for kw in labels]

    fig, ax = plt.subplots(figsize=(14, max(6, len(labels) * 0.45)))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], edgecolor='white', height=0.7)

    # Nilai di ujung bar
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=9)

    # Legend kategori
    seen_cats = {}
    for kw in labels:
        cat = kw_cat_map.get(kw, 'Lainnya')
        if cat not in seen_cats:
            seen_cats[cat] = kw_color_map.get(kw, '#607D8B')
    legend_patches = [mpatches.Patch(color=c, label=cat) for cat, c in seen_cats.items()]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=9, framealpha=0.7)

    ax.set_xlabel('Jumlah Kemunculan', fontsize=11)
    ax.set_title(f'Top {len(items)} Keyword dalam Komentar Instagram', fontsize=13, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(0, max(values) * 1.15)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"      Chart disimpan: {filepath}")


def main():
    driver = init_driver()
    try:
        login(driver, USERNAME, PASSWORD)
        comments = scrape_comments(driver, POST_URL)
        save_comments_csv(comments, OUT_COMMENTS)
        sorted_counts = count_and_save_keywords(comments, KEYWORDS, KW_CAT_MAP, OUT_KEYWORDS)
        make_chart(sorted_counts, KW_COLOR_MAP, KW_CAT_MAP, TOP_CHART_N, OUT_CHART)

        print("\n✅ Selesai! File yang dihasilkan:")
        print(f"   • {OUT_COMMENTS:<22} → semua komentar mentah")
        print(f"   • {OUT_KEYWORDS:<22} → frekuensi keyword (dengan kategori)")
        print(f"   • {OUT_CHART:<22} → bar chart top {TOP_CHART_N} keyword")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()