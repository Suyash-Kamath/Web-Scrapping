import requests
from bs4 import BeautifulSoup
import time
import re

BASE_URL = "https://www.yelu.in"
CATEGORY_URL = f"{BASE_URL}/category/car-rental"
HEADERS = {'User-Agent':'Mozilla/5.0'}


def clean(text):
    if not text or text =="-":
        return "-"
    text = re.sub(r"[\/|\n]", "," ,text)
    parts  =[   part.strip()   for part in text.split(",") if part.strip() ]
    return ", ".join(parts) if parts else "-"




def extract_company_profile(page_url):
    try:
        print(f"Visiting: {page_url}")
        profile_response = requests.get(url=page_url,headers=HEADERS,timeout=20)
        profile_response.raise_for_status()
        profile_soup = BeautifulSoup(profile_response.text,'html.parser')


        def getInfo(label):
            info_div = profile_soup.find_all('div',class_='info')
            for info in info_div:
                label_div = info.find('div', class_='label')
                if label_div and label_div.text.strip().lower()==label.lower():
                    text_div = info.find('div',class_='text')
                    if text_div:
                        links = text_div.find_all('a')
                        if links:
                            return ', '.join(link.get_text(strip=True) for link in links)
                        return text_div.get_text(" ",strip=True)
            return '-'
        address = getInfo("Address")

        mobile_phone_raw = getInfo("Mobile phone")
        contact_number_raw = getInfo("Contact number")
        website = getInfo("Website address")

        mobile_phone = clean(mobile_phone_raw)
        contact_number = clean(contact_number_raw)

        return address, mobile_phone, website, contact_number
    
    except Exception as e:
        print(f'Error Fetching profile : {e}')
        return "-","-","-","-"

        

        

                        

def scrape_list_page(page_url):
    try:
       response = requests.get(url=page_url,headers=HEADERS,timeout=10)
       response.raise_for_status()
       soup = BeautifulSoup(response.text  , 'html.parser')
       companies = soup.select('div.company.g_0')
       print(f'Found {len(companies)} in the page ')

       for company in companies:
           name_tag = company.select_one('h3 a')
           if name_tag:
               name = name_tag.text.strip()
               profile_url = BASE_URL+name_tag['href']

               address, mobile, website, contact = extract_company_profile(profile_url)
               print(f"\n🏢 Company: {name}")
               print(f"📍 Address: {address}")
               print(f"📞 Phone: {mobile}")
               print(f"🌐 Website: {website}")
               print(f"📞 Contact: {contact}")
               print("---")

               time.sleep(1)

    except Exception as e:
        print(f"❌ Error scraping list page: {e}")
    


for page_num in range(1,200):
    page_url = CATEGORY_URL if page_num ==1 else f"{CATEGORY_URL}/{page_num}"
    scrape_list_page(page_url)
    time.sleep(1)