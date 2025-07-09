import requests
from bs4 import BeautifulSoup
import time

# --- Constants ---
BASE_URL = "https://www.yelu.in"
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
HEADERS = {"User-Agent": "Mozilla/5.0"}

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

        # Helper function to extract data by label
        def get_info(label):
            info_divs = soup.find_all('div', class_='info')
            for info in info_divs:
                label_div = info.find('div', class_='label')
                if label_div and label_div.text.strip().lower() == label.lower():
                    text_div = info.find('div', class_='text')
                    return text_div.get_text(strip=True) if text_div else "-"
            return "-"

        mobile_phone = get_info("Mobile phone")
        website = get_info("Website address")

        return address, mobile_phone, website

    except Exception as e:
        print(f"    ❌ Error fetching profile: {e}")
        return "-", "-", "-"

# --- Function to Scrape One List Page ---
def scrape_list_page(page_url):
    try:
        print(f"\n📄 Scraping list page: {page_url}")
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # ✅ This selector includes companies with or without images
        companies = soup.select('div.company.g_0')

        print(f"Found {len(companies)} companies on this page")

        for company in companies:
            name_tag = company.select_one('h3 a')
            if name_tag:
                name = name_tag.text.strip()
                profile_url = BASE_URL + name_tag['href']

                # Extract details from profile
                address, phone, website = extract_company_profile(profile_url)

                print(f"\n🏢 Company: {name}")
                print(f"📍 Address: {address}")
                print(f"📞 Phone: {phone}")
                print(f"🌐 Website: {website}")
                print("---")

                # Politeness delay
                time.sleep(1)

    except Exception as e:
        print(f"❌ Error scraping list page: {e}")

# --- Main Pagination Loop ---
for page_num in range(1, 10):  # Increase range if needed (e.g., up to 199)
    page_url = CATEGORY_URL if page_num == 1 else f"{CATEGORY_URL}/{page_num}"
    scrape_list_page(page_url)
    time.sleep(2)  # Politeness delay between pages
