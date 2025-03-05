# Purpose
Scrapes TimeWellScheduled because their security is pretty questionable and it might be useful to get a list of users who work this month?.

# Limitations
- I haven't made it so you can get a specific start date.
- I haven't been able to test whether shifts properly end up in the correct schema (shown in [main.py](./main.py)) YET. Once I get a day where more than 1 person is scheduled, I can fix/verify this.
- This script is very trivial right now because I don't have a use case ATM.

# Usage
1. Clone the repo.
2. Install dependencies using `pip install -r requirements.txt`.
3. Make a .env file in the root and paste the cookies from a logged-in TWS instance as a variable called `TWS_COOKIES`.
    - Cookies should be a string of key-value pairs, keys being the cookie's name and values being the values.
    - Example: `TWS_COOKIES = '{"CompanyName":"COMPANY_HERE","Token":"TOKEN_HERE"}'`
4. Run the script, and it'll spit out all of the shifts for the current month.
    - You can filter by person by changing the `OtherLoginID` request parameter to one of the IDs found in the preview.html file.
    - The response schema can be found at the bottom of [main.py](./main.py).
5. View an HTML version of the response by opening `preview.html` which is created after you run the script.

Fin.