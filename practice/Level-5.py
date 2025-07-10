import re
import requests
import time
import csv
from bs4 import BeautifulSoup

BASE_URL = 'https://www.yelu.in'
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_FILE = "car_rental_data.csv"

def get_total_pages():
    pages_response = requests.get(CATEGORY_URL, headers=HEADERS, timeout=20)
    pages_response.raise_for_status()
    pages_soup = BeautifulSoup(pages_response.text, 'html.parser')
    page_links = pages_soup.select('div.scroller.scroller_with_ul li a.pages_no')
    pages = [int(link.text.strip()) for link in page_links if link.text.strip().isdigit()]
    maximum = max(pages) if pages else 1
    print(f"📄 Total pages detected: {maximum}")
    return maximum

def scrape_profile_page(profile_url):
    get_response = requests.get(profile_url, headers=HEADERS, timeout=20)
    get_response.raise_for_status()
    get_soup = BeautifulSoup(get_response.text, 'html.parser')

    def get_info(label):
        info_divs = get_soup.select('div.info')
        for info in info_divs:
            label_div = info.select_one('div.label')
            if label_div and label_div.text.strip().lower() == label.lower():
                text_div = info.select_one('div.text')  # ✅ Corrected line
                if text_div:
                    links = text_div.select('a')
                    if links:
                        return ", ".join(link.get_text(strip=True) for link in links)
                    return text_div.get_text(strip=True)
        return "-"

    address = get_info("Address")
    website = get_info("Website address")
    mobile = get_info("Mobile phone")
    contact = get_info("Contact number")
    return address, website, mobile, contact

def scrape_list_pages(url, writer):
    profile_response = requests.get(url, headers=HEADERS, timeout=20)
    profile_response.raise_for_status()
    profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
    companies = profile_soup.select('div.company.g_0')
    print(f"✅ Found {len(companies)} companies on {url}")  # ✅ Fixed variable
    for company in companies:
        name_tag = company.select_one('h3 a')
        if name_tag:
            name = name_tag.text.strip()
            profile_url = BASE_URL + name_tag['href']
            address, website, mobile, contact = scrape_profile_page(profile_url)
            writer.writerow([name, address, website, mobile, contact])
            print(f"📝 Saved: {name}")
            time.sleep(1)

# --- Main Execution ---
with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Address", "Website", "Mobile", "Contact"])
    total_pages = get_total_pages()
    for page_num in range(1, total_pages + 1):
        page_url = CATEGORY_URL if page_num == 1 else f"{CATEGORY_URL}/{page_num}"
        scrape_list_pages(page_url, writer)
        time.sleep(2)
