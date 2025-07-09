import requests
import time 
import re
from bs4 import BeautifulSoup

BASE_URL = 'https://www.yelu.in'
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
HEADERS = {'User-Agent':'Mozilla/5.0'}


def extract_profile(profile_url):

    personal_response = requests.get(url=profile_url,headers=HEADERS,timeout=20)
    personal_response.raise_for_status()
    personal_soup = BeautifulSoup(personal_response.text,'html.parser')



    def get_info(label):
        info_divs  = personal_soup.find_all('div',class_='info')
        for info in info_divs:
            label_div = info.find('div',class_='label')
            if label_div and label_div.text.strip().lower()==label.lower():
                text_div = info.find('div',class_='text')
                if text_div:
                    links = text_div.find_all('a')
                    if links:
                        return ', '.join(link.get_text(strip=True) for link in links)
                    return text_div.get_text(", ",strip=True)
        return "-"


    address = get_info("Address")
    website = get_info("Website address")
    mobile = get_info("Mobile phone")
    contact = get_info("Contact number")


    return address,website,mobile,contact


def scrape_list(page_url):
    profile_response = requests.get(url=page_url,headers=HEADERS,timeout=20)
    profile_response.raise_for_status()
    profile_soup = BeautifulSoup(profile_response.text,'html.parser')
    companies = profile_soup.select('div.company.g_0')
    print(f'Found {len(companies)} on the Page ')

    for company in companies:
        name_tag= company.select_one('h3 a')
        if name_tag:
            name  = name_tag.text.strip()
            profile_url = f"{BASE_URL}/{name_tag['href']}"
            address,website,mobile,contact = extract_profile(profile_url)

            print(f"\n🏢 Company: {name}")
            print(f"📍 Address: {address}")
            print(f"📞 Phone: {mobile}")
            print(f"🌐 Website: {website}")
            print(f"📞 Contact: {contact}")
            print("---")

            time.sleep(1)


def get_total_pages():
    response = requests.get(url=CATEGORY_URL,headers=HEADERS,timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    page_links = soup.select('div.scroller.scroller_with_ul li a.pages_no')
    page_numbers = []

    for link in page_links:
        num = int(link.text.strip())
        page_numbers.append(num)

    if page_numbers:
        maximum = max(page_numbers)
        print(f'Total Pages Detected {maximum}')
        return maximum
    else:
        return 1



total_pages = get_total_pages()


for page_num in range(1,total_pages+1):
    page_url = CATEGORY_URL if page_num==1 else f"{CATEGORY_URL}/{page_num}"
    scrape_list(page_url)
    time.sleep(1)

