from playwright.sync_api import sync_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -------- CONFIG --------
CMS_URL = "YOUR_CMS_URL"
CMS_USER = "YOUR_USERNAME"
CMS_PASS = "YOUR_PASSWORD"

MSN_URL = "YOUR_MSN_URL"
MSN_USER = "YOUR_USERNAME"
MSN_PASS = "YOUR_PASSWORD"

SHEET_NAME = "Video Dashboard"

# -------- GOOGLE SHEET SETUP --------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

today = datetime.now().strftime("%Y-%m-%d")

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
        count_text = page.inner_text("YOUR_VIDEO_COUNT_SELECTOR")

        browser.close()

        try:
            return int(count_text)
        except:
            return 0

# -------- FETCH DATA --------
cms_count = get_video_count(CMS_URL, CMS_USER, CMS_PASS)
msn_count = get_video_count(MSN_URL, MSN_USER, MSN_PASS)

total = cms_count + msn_count

# -------- AVOID DUPLICATES --------
existing_dates = sheet.col_values(1)

if today not in existing_dates:
    sheet.append_row([today, cms_count, msn_count, total, ""])
    print("Data added")
else:
    print("Already exists")
