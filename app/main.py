import logging
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from azure.storage.blob import BlobServiceClient

def run_scraper():
    utc_timestamp = datetime.utcnow().replace(tzinfo=None).isoformat()
    logging.basicConfig(level=logging.INFO)
    logging.info(f"⏱️ Scraper started at {utc_timestamp}")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    vendor_sources = {
        "Ivanti Forums": "https://forums.ivanti.com/",
        "Microsoft Q&A": "https://learn.microsoft.com/en-us/answers/topics/azure.html",
        "Microsoft Tech Community": "https://techcommunity.microsoft.com/t5/azure/ct-p/Azure",
        "Spiceworks": "https://community.spiceworks.com/",
        "VMware Communities": "https://communities.vmware.com/t5/VMware-vSphere/ct-p/2002",
        "PatchMyPC Blog": "https://patchmypc.com/blog",
        "ITNinja": "https://www.itninja.com/software/",
        "BleepingComputer Forums": "https://www.bleepingcomputer.com/forums/"
    }

    keywords = ["ivanti", "vpn", "azure", "login", "incident", "patch", "endpoint", "performance", "authentication", "error", "issue"]

    data = {
        "date": utc_timestamp,
        "entries": []
    }

    for vendor, url in vendor_sources.items():
        try:
            logging.info(f"🔍 Scraping {vendor}")
            driver.get(url)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True).lower()
                if any(kw in text for kw in keywords):
                    full_url = urljoin(url, a['href'])
                    tag = next((kw for kw in keywords if kw in text), "general")
                    data["entries"].append({
                        "vendor": vendor,
                        "title": a.get_text(strip=True),
                        "url": full_url,
                        "tag": tag
                    })

        except Exception as e:
            logging.error(f"❌ Error scraping {vendor}: {e}")
            continue

    driver.quit()

    filename = f"thinktank_knowledge_{datetime.today().strftime('%Y-%m-%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    try:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container="community-data", blob=filename)

        with open(filename, "rb") as file:
            blob_client.upload_blob(file, overwrite=True)

        logging.info(f"📤 Uploaded to Azure Blob Storage: {filename}")
    except Exception as e:
        logging.error(f"❌ Failed to upload to Blob Storage: {e}")

if __name__ == "__main__":
    run_scraper()

