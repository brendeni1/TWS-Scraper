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

def extractShifts(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    shifts_by_date = {}
    current_year = datetime.now().year
    
    # Extract employee ID mapping from option values
    employee_ids = {}
    for option in soup.select('select#OtherLoginID option'):
        if option.has_attr('value') and option.text.strip():
            employee_ids[option.text.strip()] = option['value']
    
    # Find all shift entries
    for shift_entry in soup.find_all('td', style=re.compile('background:#efef7d')):
        name_tag = shift_entry.find('p')
        dept_tag = name_tag.find_next('p') if name_tag else None
        time_tags = shift_entry.find_all('font')
        date_tag = shift_entry.find_previous("div", class_="cal-date")
        
        if name_tag and dept_tag and len(time_tags) == 2 and date_tag:
            employee_name = name_tag.get_text(strip=True)
            department = dept_tag.get_text(strip=True)
            start_time = time_tags[0].get_text(strip=True).replace("To", "").strip()
            end_time = time_tags[1].get_text(strip=True)
            date_text = date_tag.get_text(strip=True)
            employee_id = employee_ids.get(employee_name, "Unknown")
            
            date = f"{date_text}, {current_year}"
            
            if date not in shifts_by_date:
                shifts_by_date[date] = {"date": date, "shifts": []}
            
            shifts_by_date[date]["shifts"].append({
                "employeeId": int(employee_id) if employee_id.isdigit() else None,
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

shiftsFormatted = extractShifts(response.text)

print(shiftsFormatted)

# SCHEMA = [
#     {
#         "date": "Mar X, 20XX",
#         "shifts": [
#             {
#                 "employeeId": NUM,
#                 "employeeName": STR,
#                 "department": STR,
#                 "startDate": STR,
#                 "endDate": STR,
#             }
#         ],
#     },
#     {
#         "date": "Mar 4, 2025",
#         "shifts": [
#             {
#                 ...
#             }
#         ],
#     }
# ]