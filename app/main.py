import logging
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from azure.storage.blob import BlobServiceClient

# Set up logging
logging.basicConfig(level=logging.INFO)

def run_scraper():
    utc_timestamp = datetime.utcnow().isoformat()
    logging.info(f"⏱️ Scraper started at {utc_timestamp}")

    # ✅ Chrome options for headless Linux containers (Azure)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        vendor_sources = {
            "Ivanti Forums": "https://forums.ivanti.com/",
            "Microsoft Q&A": "https://learn.microsoft.com/en-us/answers/",
            "Spiceworks": "https://community.spiceworks.com/",
            "VMware Communities": "https://communities.vmware.com/",
            "Citrix Discussions": "https://discussions.citrix.com/",
            "Stack Overflow": "https://stackoverflow.com/questions/tagged/ivanti",
            "Reddit r/sysadmin": "https://www.reddit.com/r/sysadmin/",
            "TechNet Forums (Archived)": "https://social.technet.microsoft.com/Forums/",
            "Dell Support Community": "https://www.dell.com/community/",
            "HP Community": "https://h30434.www3.hp.com/",
            "Lenovo Forums": "https://forums.lenovo.com/",
            "Cisco Community": "https://community.cisco.com/",
            "Fortinet Forums": "https://community.fortinet.com/",
            "Palo Alto Networks Community": "https://live.paloaltonetworks.com/",
            "Aruba Networks Community": "https://community.arubanetworks.com/",
            "Juniper Networks Forums": "https://forums.juniper.net/",
            "Zebra Developer Portal": "https://developer.zebra.com/forum",
            "Splunk Answers": "https://community.splunk.com/",
            "ServiceNow Community": "https://community.servicenow.com/",
            "ManageEngine PitStop": "https://pitstop.manageengine.com/portal/en/community",
            "Nutanix Community": "https://next.nutanix.com/",
            "Sophos Community": "https://community.sophos.com/"
        }

        all_data = []

        for vendor, url in vendor_sources.items():
            logging.info(f"🔍 Scraping: {vendor}")
            try:
                driver.get(url)
                time.sleep(5)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links:
                    full_url = urljoin(url, link['href'])
                    all_data.append({
                        'vendor': vendor,
                        'text': link.text.strip().replace(',', ' '),
                        'url': full_url
                    })
            except Exception as e:
                logging.warning(f"⚠️ Failed to scrape {vendor}: {e}")

        # Save to CSV locally
        csv_filename = "scraped_links.csv"
        with open(csv_filename, "w", encoding="utf-8") as f:
            f.write("vendor,text,url\n")
            for entry in all_data:
                f.write(f"{entry['vendor']},{entry['text']},{entry['url']}\n")

        # ✅ Upload to Azure Blob
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "scraper-data"
        blob_name = f"scraped_links_{int(time.time())}.csv"

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(csv_filename, "rb") as data:
            blob_client.upload_blob(data)

        logging.info(f"✅ Uploaded to Azure Blob: {blob_name}")

    except Exception as e:
        logging.error("❌ Critical error during scraping", exc_info=True)

    finally:
        driver.quit()
        logging.info("🛑 Browser session closed. Scraper complete.")

if __name__ == "__main__":
    run_scraper()



