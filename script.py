from playwright.sync_api import sync_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
date_for_entry = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# -------- CONFIG --------
CMS_URL = "https://denmark.timesinternet.in/reporting/cms-analytics/"
CMS_USER = "mohit.singh1@timesinternet.in"
CMS_PASS = "sambhavya#navya1201"

MSN_URL = "https://www.msn.com/en-in/partnerhub/login?partner_type=c2s&rurl=%2Fen-in%2Fpartnerhub%2F"
MSN_USER = "mohit.singh1@timesinternet.in"
MSN_PASS = "sambhavya#navya1201"

SHEET_NAME = "Video Dashboard"

# -------- GOOGLE SHEET SETUP --------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1
if date_for_entry not in existing_dates:
    sheet.append_row([date_for_entry, cms_count, msn_count, total, ""])

# -------- SCRAPER FUNCTION --------
def get_video_count(url, username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)

        # ---- LOGIN (UPDATE SELECTORS) ----
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')

        page.wait_for_timeout(5000)

        # ---- EXTRACT VIDEO COUNT ----
        # Replace selector based on your dashboard
        count_text = page.inner_text("media video")

        browser.close()

        try:
            return int(count_text)
        except:
            return 0

# -------- FETCH DATA --------
def get_cms_video_count():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(CMS_URL)

        page.fill('input[name="username"]', CMS_USER)
        page.fill('input[name="password"]', CMS_PASS)
        page.click('button[type="submit"]')

        page.wait_for_load_state("networkidle")
        page.wait_for_selector("text=Media Video", timeout=60000)

        elements = page.query_selector_all("div")

        for el in elements:
            text = el.inner_text()
            if "Media Video" in text:
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])

        return 0
def get_msn_video_count():
    from playwright.sync_api import sync_playwright
    import re

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(MSN_URL)

        # Login (update if needed)
        page.fill('input[type="email"]', MSN_USER)
        page.fill('input[type="password"]', MSN_PASS)
        page.click('button[type="submit"]')

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(8000)

        elements = page.query_selector_all("div")

        for el in elements:
            text = el.inner_text()
            if "Video" in text or "Videos" in text:
                numbers = re.findall(r'\d+', text)
                if numbers:
                    browser.close()
                    return int(numbers[0])

        browser.close()
        return 0
# -------- AVOID DUPLICATES --------
existing_dates = sheet.col_values(1)

if today not in existing_dates:
    sheet.append_row([today, cms_count, msn_count, total, ""])
    print("Data added")
else:
    print("Already exists")
