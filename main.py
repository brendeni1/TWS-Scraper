import os
import json
import re

from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup

import requests
import requests.cookies

PREVIEW_FILE_NAME = "preview.html"
TWS_COOKIE_NAME = "TWS_COOKIES"

def extract_shifts(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    shifts_by_date = {}
    current_year = datetime.now().year
    
    # Find all shift entries in the table
    for shift_entry in soup.find_all('td', style=re.compile('background:#efef7d')):
        name_tag = shift_entry.find('p')
        dept_tag = name_tag.find_next('p') if name_tag else None
        start_time_tag = shift_entry.find('font')
        end_time_tag = start_time_tag.find_next('font') if start_time_tag else None
        date_tag = shift_entry.find_previous("div", class_="cal-date")
        
        if name_tag and dept_tag and start_time_tag and end_time_tag and date_tag:
            employee_name = name_tag.get_text(strip=True)
            department = dept_tag.get_text(strip=True)
            start_time = start_time_tag.get_text(strip=True).replace("To", "").strip()
            end_time = end_time_tag.get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            
            # Append the most realistic year
            date = f"{date_text}, {current_year}"
            
            if date not in shifts_by_date:
                shifts_by_date[date] = {"date": date, "shifts": []}
            
            shifts_by_date[date]["shifts"].append({
                "employeeName": employee_name,
                "department": department,
                "startDate": f"{date} {start_time}",
                "endDate": f"{date} {end_time}",
            })
    
    return list(shifts_by_date.values())

load_dotenv()

session = requests.Session()

cookieString = os.getenv(TWS_COOKIE_NAME)

cookieDict = json.loads(s=cookieString)

cookieJar: requests.cookies.RequestsCookieJar = requests.cookies.cookiejar_from_dict(
    cookie_dict=cookieDict
)

response = session.get(
    url="https://ca.timewellscheduled.com/New/Schedule/view_my_schedule.asp",
    params={
        "OtherLoginID": 0
    },
    cookies=cookieJar
)

with open(PREVIEW_FILE_NAME, "w") as file:
    file.write(response.text)

shiftsFormatted = extract_shifts(response.text)

print(shiftsFormatted)

# SCHEMA = [
#     {
#         "date": "Mar 3, 2025",
#         "shifts": [
#             {
#                 "employeeName": "BRIAN BROUILLETTE",
#                 "department": "PRO SHOP",
#                 "startDate": "Mar 3, 2025 9:00a",
#                 "endDate": "Mar 3, 2025 5:00p",
#             }
#         ],
#     },
#     {
#         "date": "Mar 4, 2025",
#         "shifts": [
#             {
#                 "employeeName": "BRIAN BROUILLETTE",
#                 "department": "PRO SHOP",
#                 "startDate": "Mar 4, 2025 9:00a",
#                 "endDate": "Mar 4, 2025 4:45p",
#             }
#         ],
#     }
# ]