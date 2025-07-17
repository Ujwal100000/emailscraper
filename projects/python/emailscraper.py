import requests
from bs4 import BeautifulSoup
import re
import csv
import tldextract

# Custom user agent to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# Regex to find clean emails with word boundaries
EMAIL_REGEX = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

# Extract emails from a given URL
def get_emails_from_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')
        raw_emails = re.findall(EMAIL_REGEX, text)
        cleaned_emails = {email.strip().lower() for email in raw_emails}
        return cleaned_emails
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return set()

# Tries to find contact page from homepage links
def find_contact_page(base_url):
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=10)
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

# Normalize website URL and extract base domain
def normalize_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    extracted = tldextract.extract(url)
    domain = ".".join(part for part in [extracted.domain, extracted.suffix] if part)
    return url, domain

# Main scraping function
def scrape_emails_from_websites(websites, output_csv="emails.csv"):
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Website', 'Emails'])

        for website in websites:
            print(f"\n🔍 Processing: {website}")
            base_url, domain = normalize_url(website)
            all_emails = set()

            # Scrape from homepage
            homepage_emails = get_emails_from_url(base_url)
            all_emails.update(homepage_emails)

            # Scrape from contact page if available
            contact_url = find_contact_page(base_url)
            if contact_url:
                print(f"   ➤ Found contact page: {contact_url}")
                contact_emails = get_emails_from_url(contact_url)
                all_emails.update(contact_emails)

            print(f"   📧 Found {len(all_emails)} emails")
            writer.writerow([domain, ", ".join(sorted(all_emails))])

    print(f"\n✅ Scraping complete. Results saved to {output_csv}")

# ----------------------------------------
# List of websites to scrape
# ----------------------------------------

if __name__ == "__main__":
    websites = [
        "http://www.wrp.it",
        "http://www.pyjamahr.com",
        "http://www.niktorinc.com",
        "http://www.officialblackwallstreet.com",
        "http://www.professional.me",
        "http://www.omniskope.com",
        "http://www.airapps.co",
        "http://www.afrotech.com",
        "http://www.edzsystems.com",
        "http://www.jsrtechconsulting.com",
        "http://www.groupainc.com",
        "http://www.theseattledataguy.com",
        "http://www.headwaytek.com",
        "http://www.outcomelogix.com",
        "http://www.neetcode.io",
        "http://www.crowdplat.com",
        "http://www.powerbi.tips"
    ]
    scrape_emails_from_websites(websites)
