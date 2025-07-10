import requests
from bs4 import BeautifulSoup
import time
import re
import csv

# --- Constants ---
BASE_URL = "https://www.yelu.in"
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_FILE = "car_rental_companies.csv"

# --- Clean Phone Numbers ---
def clean_numbers(text):
    if not text or text == "-":
        return "-"
    text = re.sub(r"[\/\|\n]", ",", text)
    parts = [part.strip() for part in text.split(",") if part.strip()]
    return ", ".join(parts) if parts else "-"

# --- Detect Total Pages ---
def get_total_pages():
    try:
        res = requests.get(CATEGORY_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')   
        page_links = soup.select('div.scroller_with_ul li a.pages_no')
        page_numbers = [int(link.text.strip()) for link in page_links if link.text.strip().isdigit()]
        max_page = max(page_numbers) if page_numbers else 1
        print(f"📄 Total pages detected: {max_page}")
        return max_page
    except Exception as e:
        print(f"❌ Error detecting pages: {e}")
        return 1

# --- Extract Profile Data ---
def extract_company_profile(profile_url):
    try:
        res = requests.get(profile_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        address_elem = soup.find('div', id='company_address')
        address = address_elem.get_text(strip=True) if address_elem else "-"

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

        mobile = clean_numbers(get_info("Mobile phone"))
        contact = clean_numbers(get_info("Contact number"))
        website = get_info("Website address")

        return address, mobile, website, contact
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return "-", "-", "-", "-"

# --- Scrape and Write to CSV ---
def scrape_list_page(page_url, writer):
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        companies = soup.select('div.company.g_0')
        print(f"✅ Found {len(companies)} companies on {page_url}")

        for company in companies:
            name_tag = company.select_one('h3 a')
            if name_tag:
                name = name_tag.text.strip()
                profile_url = BASE_URL + name_tag['href']
                address, mobile, website, contact = extract_company_profile(profile_url)

                # Write row
                writer.writerow([name, address, mobile, website, contact])

                print(f"📝 Saved: {name}")
                time.sleep(1)
    except Exception as e:
        print(f"❌ Error scraping page: {e}")

# --- Main Execution with CSV Output ---
with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Address', 'Mobile Phone', 'Website', 'Contact Number'])

    total_pages = get_total_pages()
    for page_num in range(1, total_pages + 1):
        page_url = CATEGORY_URL if page_num == 1 else f"{CATEGORY_URL}/{page_num}"
        scrape_list_page(page_url, writer)
        time.sleep(2)

print("✅ Scraping completed and data saved to CSV.")
