import requests
from bs4 import BeautifulSoup
import csv
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Setup session with retry logic ---
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=2)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# --- Constants ---
BASE_URL = "https://www.yelu.in"
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
OUTPUT_CSV = "car_rental_filtered_listings.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# --- Extract from Profile Page ---
def extract_from_profile(url):
    try:
        print(f"    Fetching profile: {url}")
        res = session.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Check pagination info on first page
        if "page/1" in url or url.endswith("/category/car-rental"):
            check_pagination_info(soup)

        # Helper function to extract info by label
        def find_info_by_label(label_text):
            info_divs = soup.find_all('div', class_='info')
            for info_div in info_divs:
                label_div = info_div.find('div', class_='label')
                if label_div and label_div.get_text(strip=True).lower() == label_text.lower():
                    text_div = info_div.find('div', class_='text')
                    if text_div:
                        # Handle different text structures
                        if text_div.find('a'):
                            return text_div.find('a').get_text(strip=True)
                        else:
                            return text_div.get_text(strip=True)
            return "-"

        # Extract company name
        company_name_elem = soup.find('div', id='company_name')
        company_name = company_name_elem.get_text(strip=True) if company_name_elem else "-"

        # Extract address
        address_elem = soup.find('div', id='company_address')
        address = address_elem.get_text(strip=True) if address_elem else "-"

        # Extract other information using the helper function
        contact_number = find_info_by_label("Contact number")
        mobile_phone = find_info_by_label("Mobile phone")
        website_address = find_info_by_label("Website address")

        # Extract company manager from extra_info section
        company_manager = "-"
        extra_info = soup.find('div', class_='extra_info')
        if extra_info:
            info_divs = extra_info.find_all('div', class_='info')
            for info_div in info_divs:
                label_div = info_div.find('div', class_='label')
                if label_div and label_div.get_text(strip=True).lower() == "company manager":
                    # Company manager text is directly after the label div
                    company_manager = info_div.get_text(strip=True).replace("Company manager", "").strip()
                    break

        return {
            "Company Name": company_name,
            "Address": address,
            "Contact Number": contact_number,
            "Mobile Phone": mobile_phone,
            "Website Address": website_address,
            "Company Manager": company_manager,
            "Profile URL": url
        }

    except Exception as e:
        print(f"    ⚠️ Error scraping profile {url}: {e}")
        return {}

# --- Check pagination info ---
def check_pagination_info(soup):
    """Check pagination information to understand total pages/results"""
    try:
        # Look for pagination info
        pagination_info = soup.select('.pagination, .pager, .results-info')
        if pagination_info:
            print(f"  Pagination info found: {pagination_info[0].get_text(strip=True)}")

        # Look for total results count
        results_text = soup.get_text()
        if "results" in results_text.lower():
            lines = results_text.split('\n')
            for line in lines:
                if "result" in line.lower() and any(char.isdigit() for char in line):
                    print(f"  Results info: {line.strip()}")
                    break
    except Exception as e:
        print(f"  Could not extract pagination info: {e}")

# --- Scrape List Page and Profile ---
def scrape_list_page(url):
    try:
        print(f"  Fetching list page: {url}")
        res = session.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Updated selector to match both with_img and without img companies
        companies = soup.select('div.company.g_0')
        print(f"  Found {len(companies)} companies on this page")

        # Debug: Let's also check what other company classes exist
        all_companies = soup.select('div.company')
        print(f"  Debug: Total div.company found: {len(all_companies)}")

        # Check different variations
        with_img = soup.select('div.company.with_img.g_0')
        without_img = soup.select('div.company.g_0:not(.with_img)')
        print(f"  Debug: with_img.g_0: {len(with_img)}, without with_img: {len(without_img)}")

        if len(companies) == 0:
            print("  No companies found - might have reached end of pages")
            # Let's check if page exists but has different structure
            page_content = soup.get_text()
            if "No results found" in page_content or "404" in page_content:
                print("  Page indicates no results or 404")
            return []

        listings = []
        for i, company in enumerate(companies, 1):
            try:
                # Extract profile URL
                name_tag = company.select_one('h3 a')
                if name_tag and name_tag.get('href'):
                    profile_url = BASE_URL + name_tag['href']
                    print(f"  [{i}/{len(companies)}] Processing: {name_tag.get_text(strip=True)}")

                    # Extract profile data
                    data = extract_from_profile(profile_url)
                    if data and data.get("Company Name") != "-":
                        listings.append(data)
                        print(f"    ✅ Successfully extracted data for: {data['Company Name']}")
                    else:
                        print(f"    ❌ Failed to extract data")

                    # Add delay between profile requests
                    time.sleep(1)
                else:
                    print(f"  ⚠️ No profile URL found for company {i}")

            except Exception as e:
                print(f"  ⚠️ Error processing company {i}: {e}")
                continue

        return listings

    except Exception as e:
        print(f"  ❌ Error scraping list page {url}: {e}")
        return []

# --- Main Execution ---
def main():
    print("🚀 Starting car rental scraper...")
    print(f"Target: {CATEGORY_URL}")

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            "Company Name", "Address", "Contact Number", "Mobile Phone",
            "Website Address", "Company Manager", "Profile URL"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        total_scraped = 0

        for page_num in range(1, 200):  # Increased to 500 pages to capture all 3962 listings
            # Construct page URL
            if page_num == 1:
                page_url = CATEGORY_URL
            else:
                page_url = f"{CATEGORY_URL}/{page_num}"

            print(f"\n📄 Scraping page {page_num}/199")

            try:
                rows = scrape_list_page(page_url)

                if not rows:
                    print(f"No data found on page {page_num}. Stopping scraper.")
                    break

                # Write rows to CSV
                writer.writerows(rows)
                f.flush()  # Ensure data is written to file

                total_scraped += len(rows)
                print(f"✅ Page {page_num} completed. Added {len(rows)} listings. Total: {total_scraped}")

            except Exception as e:
                print(f"❌ Error on page {page_num}: {e}")
                continue

            # Add delay between pages
            print(f"⏳ Waiting before next page...")
            time.sleep(2)

    print(f"\n🎉 Scraping completed! Total listings scraped: {total_scraped}")
    print(f"📁 Data saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
