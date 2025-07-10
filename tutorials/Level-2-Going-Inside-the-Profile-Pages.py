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

        # Helper function to extract by label
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

# --- Scrape List Page ---
response = requests.get(CATEGORY_URL, headers=HEADERS)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')

companies = soup.find_all('div', class_='company with_img g_0')
print(f"Found {len(companies)} companies")

# --- Loop Through Companies ---
for company in companies:
    name_tag = company.find('h3').find('a')
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
