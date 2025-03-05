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

def extractShifts(htmlContent: str):
    soup = BeautifulSoup(htmlContent, 'html.parser')
    shiftsByDate = {}
    currentYear = datetime.now().year
    
    # Extract employee ID mapping from option values
    employeeIds = {}
    for option in soup.find_all('option'):
        if option.has_attr('value') and option.text.strip():
            employeeIds[option.text.strip()] = option['value']
    
    # Find all shift entries in the table
    for shiftEntry in soup.find_all('td', style=re.compile('background:#efef7d')):
        nameTag = shiftEntry.find('p')
        deptTag = nameTag.find_next('p') if nameTag else None
        startTimeTag = shiftEntry.find('font')
        endTimeTag = startTimeTag.find_next('font') if startTimeTag else None
        dateTag = shiftEntry.find_previous("div", class_="cal-date")
        
        if nameTag and deptTag and startTimeTag and endTimeTag and dateTag:
            employeeName = nameTag.get_text(strip=True)
            department = deptTag.get_text(strip=True)
            startTime = startTimeTag.get_text(strip=True).replace("To", "").strip()
            endTime = endTimeTag.get_text(strip=True)
            dateText = dateTag.get_text(strip=True)
            employeeId = employeeIds.get(employeeName, "Unknown")
            
            # Append the most realistic year
            date = f"{dateText}, {currentYear}"
            
            if date not in shiftsByDate:
                shiftsByDate[date] = {"date": date, "shifts": []}
            
            shiftsByDate[date]["shifts"].append({
                "employeeId": int(employeeId),
                "employeeName": employeeName,
                "department": department,
                "startDate": f"{date} {startTime}",
                "endDate": f"{date} {endTime}",
            })
    
    return list(shiftsByDate.values())


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