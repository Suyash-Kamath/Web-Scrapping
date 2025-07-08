import time,requests
from bs4 import BeautifulSoup


url='https://www.yelu.in/category/car-rental'

headers={"User-Agent":"Mozilla/5.0"}
response = requests.get(url=url,headers=headers,timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text,'html.parser')
companies = soup.find_all('div',class_='company with_img g_0')
print(f"Found {len(companies)} in the Page ")



def extract_details(profile_url):

    profile_response = requests.get(url=profile_url,headers=headers,timeout = 10)
    profile_response.raise_for_status()

    profile_soup = BeautifulSoup(profile_response.text,'html.parser')
    
    
    def get_info(label):
        info_div = profile_soup.find_all('div','info')
        for info in info_div:
            label_div = info.find('div',class_='label')
            if label_div and label_div.text.strip().lower() == label.lower():
                text_div = info.find('div',class_='text')
                return text_div.text.strip() if text_div else "-"
        return "-"
        


        

    address = get_info('Address')
    website = get_info('Website adress')
    mobile_number = get_info('Mobile phone')
    contact_number = get_info('Contact number')

    return address,website,mobile_number,contact_number


for company in companies:
    name_tag = company.find('h3').find('a')
    if name_tag:
        name = name_tag.text.strip()
        profile_url = 'https://www.yelu.in'+name_tag['href']
        
        address,website,mobile_number,contact_number = extract_details(profile_url)
        print(f'Name of the Organisation: {name}')
        print(f"Address: {address}")
        print(f'Website: {website}')
        print(f'Mobile Number: {mobile_number}')
        print(f'Contact Number: {contact_number}')
        print('--')

        time.sleep(1)

