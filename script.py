from playwright.sync_api import sync_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import re

# -------- DATE --------
date_for_entry = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# -------- CONFIG --------
CMS_URL = "https://denmark.timesinternet.in/reporting/cms-analytics/#/reporting/cms-analytics/sections"
CMS_USER = "mohit.singh1@timesinternet.in"
CMS_PASS = "sambhavya#navya1201"

MSN_URL = "https://www.msn.com/en-in/partnerhub/analytics/content/overview"
MSN_USER = "mohit.singh1@timesinternet.in"
MSN_PASS = "sambhavya#navya1201"

SHEET_NAME = "Video Dashboard"

# -------- GOOGLE SHEET SETUP --------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# -------- CMS FUNCTION --------
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
                numbers = re.findall(r'\d+', text)
                if numbers:
                    browser.close()
                    return int(numbers[0])

        browser.close()
        return 0

# -------- MSN FUNCTION --------
def get_msn_video_count():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(MSN_URL)

        # Login
        page.fill('input[type="email"]', MSN_USER)
        page.fill('input[type="password"]', MSN_PASS)
        page.click('button[type="submit"]')

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(8000)

        # 👉 Select Yesterday
        try:
            page.click("text=Today")
            page.wait_for_timeout(2000)
            page.click("text=Yesterday")
            page.wait_for_timeout(5000)
        except:
            pass  # अगर नहीं मिला तो skip

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

# -------- FETCH DATA --------
try:
    cms_count = get_cms_video_count()
except:
    cms_count = 0

try:
    msn_count = get_msn_video_count()
except:
    msn_count = 0

total = cms_count + msn_count

print("CMS:", cms_count, "MSN:", msn_count, "TOTAL:", total)

# -------- GOOGLE SHEET UPDATE --------
existing_dates = sheet.col_values(1)

if date_for_entry not in existing_dates:
    sheet.append_row([date_for_entry, cms_count, msn_count, total, ""])
    print("✅ Data added")
else:
    print("⚠️ Already exists")
