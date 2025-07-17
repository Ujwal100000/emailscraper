import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import re
import csv
import tldextract

# Regex for emails
EMAIL_REGEX = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

# Google Sheets Setup
SHEET_NAME = 'YourSheetNameHere'  # Change this to your sheet name
WORKSHEET_TAB = 'Sheet1'  # Usually Sheet1 unless renamed


# Authentication
def get_worksheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME)
    return sheet.worksheet(WORKSHEET_TAB)


# Email extraction
def get_emails_from_url(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')
        raw_emails = re.findall(EMAIL_REGEX, text)
        return {email.strip().lower() for email in raw_emails}
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return set()


def find_contact_page(base_url):
    try:
        response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].lower()
            if 'contact' in href:
                if href.startswith('http'):
                    return href
                elif href.startswith('/'):
                    return base_url.rstrip('/') + href
        return None
    except:
        return None


def normalize_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    extracted = tldextract.extract(url)
    domain = ".".join(part for part in [extracted.domain, extracted.suffix] if part)
    return url, domain


# Scrape and update Google Sheet
def scrape_and_update_sheet():
    ws = get_worksheet()
    rows = ws.get_all_values()

    # Assumes first column = URL, second column = Status, third column = Emails
    header = rows[0]
    data = rows[1:]

    for idx, row in enumerate(data, start=2):  # Start at row 2 in the sheet
        url = row[0].strip()
        status = row[1].strip() if len(row) > 1 else ""

        if status.lower() == 'done':
            continue  # Skip already processed

        print(f"\n🔍 Processing: {url}")
        base_url, domain = normalize_url(url)
        all_emails = set()

        all_emails.update(get_emails_from_url(base_url))

        contact_url = find_contact_page(base_url)
        if contact_url:
            print(f"   ➤ Found contact page: {contact_url}")
            all_emails.update(get_emails_from_url(contact_url))

        print(f"   📧 Found {len(all_emails)} emails")

        # Update sheet
        ws.update_cell(idx, 2, 'Done')
        ws.update_cell(idx, 3, ", ".join(sorted(all_emails)))

    print("\n✅ Scraping complete and sheet updated!")


# Run the script
if __name__ == "__main__":
    scrape_and_update_sheet()
