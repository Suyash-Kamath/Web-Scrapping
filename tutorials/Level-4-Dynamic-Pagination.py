import requests
from bs4 import BeautifulSoup
import time
import re

# --- Constants ---
BASE_URL = "https://www.yelu.in"
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# --- Helper to clean and split multiple phone numbers if needed ---
def clean_numbers(text):
    if not text or text == "-":
        return "-"
    text = re.sub(r"[\/\|\n]", ",", text)  # Replace separators with commas
    parts = [part.strip() for part in text.split(",") if part.strip()]
    return ", ".join(parts) if parts else "-"

# --- Dynamic Pagination Detector ---
def get_total_pages():
    try:
        res = requests.get(CATEGORY_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        page_links = soup.select('div.scroller_with_ul li a.pages_no')
        page_numbers = []

        for link in page_links:
            try:
                num = int(link.text.strip())
                page_numbers.append(num)
            except:
                continue

        if page_numbers:
            max_page = max(page_numbers)
            print(f"📄 Total pages detected: {max_page}")
            return max_page
        else:
            print("⚠️ No pagination found, defaulting to 1 page")
            return 1
    except Exception as e:
        print(f"❌ Error detecting total pages: {e}")
        return 1

# --- Function to Extract Data from Profile Page ---
def extract_company_profile(profile_url):
    try:
        print(f"  🔍 Visiting: {profile_url}")
        res = requests.get(profile_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Extract address
        address_elem = soup.find('div', id='company_address')
        address = address_elem.get_text(strip=True) if address_elem else "-"

        # Helper to get info by label
        def get_info(label):
            info_divs = soup.find_all('div', class_='info')
            for info_div in info_divs:
                label_div = info_div.find('div', class_='label')
                if label_div and label_div.text.strip().lower() == label.lower():
                    text_div = info_div.find('div', class_='text')
                    if text_div:
                        links = text_div.find_all('a')
                        if links:
                            return ", ".join(link.get_text(strip=True) for link in links)
                        return text_div.get_text(" ", strip=True)
            return "-"

        mobile_phone_raw = get_info("Mobile phone")
        contact_number_raw = get_info("Contact number")
        website = get_info("Website address")

        mobile_phone = clean_numbers(mobile_phone_raw)
        contact_number = clean_numbers(contact_number_raw)

        return address, mobile_phone, website, contact_number

    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return "-", "-", "-", "-"

# --- Scrape One List Page ---
def scrape_list_page(page_url):
    try:
        print(f"\n📄 Scraping list page: {page_url}")
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        companies = soup.select('div.company.g_0')
        print(f"✅ Found {len(companies)} companies on this page")

        for company in companies:
            name_tag = company.select_one('h3 a')
            if name_tag:
                name = name_tag.text.strip()
                profile_url = BASE_URL + name_tag['href']

                address, phone, website, contact_number = extract_company_profile(profile_url)

                print(f"\n🏢 Company: {name}")
                print(f"📍 Address: {address}")
                print(f"📞 Phone: {phone}")
                print(f"🌐 Website: {website}")
                print(f"📞 Contact: {contact_number}")
                print("---")

                time.sleep(1)

    except Exception as e:
        print(f"❌ Error scraping list page: {e}")

# --- Main Loop: Auto-detect Pagination ---
total_pages = get_total_pages()
for page_num in range(1, total_pages + 1):
    page_url = CATEGORY_URL if page_num == 1 else f"{CATEGORY_URL}/{page_num}"
    scrape_list_page(page_url)
    time.sleep(2)
