import requests
from bs4 import BeautifulSoup

url = "https://www.yelu.in/category/car-rental"
headers = {"User-Agent":"Mozilla/5.0"}

response = requests.get(url=url,headers=headers)
print(f'Response Code: {response.raise_for_status()}')


soup = BeautifulSoup(response.text,'html.parser')

companies = soup.find_all('div',class_='company with_img g_0')

print(f"Found {len(companies)} in the page")

for company in companies:
    name_tag = company.find('h3').find('a')
    if name_tag:
        name = name_tag.text.strip()
        profile_url = 'https://yelu.in' + name_tag['href']

        print(f"🏢 Company Name: {name}")
        print(f"🔗 Profile URL: {profile_url}")
        print("---")