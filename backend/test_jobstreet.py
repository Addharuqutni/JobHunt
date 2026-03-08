import requests
from bs4 import BeautifulSoup
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
}
url = "https://www.jobstreet.co.id/id/job-search/react-developer-jobs"

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, 'html.parser')

# Check titles
headings = soup.find_all(['h1', 'h2', 'h3'])
print("Headings found:", len(headings))
for h in headings[:5]:
    print(h.text.strip())

# Check for NEXT_DATA
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    print("Found Next.js data block")
else:
    print("No Next.js block found, might be a different framework or blocked")
    # let's write output
    with open("jobstreet_dump.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        print("Written to jobstreet_dump.html")
