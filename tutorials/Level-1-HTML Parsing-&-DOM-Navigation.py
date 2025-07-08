import requests
from bs4 import BeautifulSoup

# Step 1: Set the URL and headers
url = "https://www.yelu.in/category/car-rental"
headers = {"User-Agent": "Mozilla/5.0"}

# Step 2: Send request (skip certificate verification due to Seqrite)
response = requests.get(url, headers=headers)
print(f"Response status: {response.status_code}")  # 200 means success

# Step 3: Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Optional: Print the formatted HTML (use only when debugging)
# print(soup.prettify())

# Step 4: Extract companies (those with logos/images)
companies = soup.find_all("div", class_="company with_img g_0")
print(f"\n🔍 Found {len(companies)} companies with images.")

# Step 5: Loop through each company and extract name + profile URL
for company in companies:
    name_tag = company.find("h3").find("a")

    if name_tag:
        name = name_tag.text.strip()
        profile_url = "https://www.yelu.in" + name_tag['href']

        print(f"🏢 Company Name: {name}")
        print(f"🔗 Profile URL: {profile_url}")
        print("---")
