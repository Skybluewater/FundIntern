import requests
import json
from datetime import datetime
from dataclasses import asdict
from data.announcement import Announcement, AnnouncementSet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO
from extractor.pdf_extractor import PDFExtractor
from extractor.xlsx_extractor import XLSXExtractor


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def get_announcement(index_name: str, period: str = "5y") -> AnnouncementSet:

    # Define the URL of the CSIndex website
    total_page = 1
    page_num = 1

    set = None

    while page_num <= total_page:
        url = f"https://www.csindex.com.cn/csindex-home/search/search-content?lang=cn&searchInput={index_name}&pageNum={page_num}&pageSize=30&sortField=date&dateRange={period}&contentType=announcement"

        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            import json
            content = json.loads(response.text)
            # print(content)
            # Extract the announcement data from the HTML content
            if page_num == 1:
                set = AnnouncementSet(index_name, content["total"], content["pageSize"], content["size"], content["currentPage"], content["code"], [])
                total_page = content["size"]
            
            for item in content["data"]:
                if item["itemType"] != "announcement" or "指数定期调整结果的公告" not in item["headline"]:
                    continue
                announcement = Announcement(item["headline"], datetime.strptime(item["itemDate"], "%Y-%m-%d"), item["id"], "", "", None, set)
                set.announcements.append(announcement)
                annoucement_handler(announcement)
        
        else:
            print("Failed to retrieve data from CSIndex website.")
        
        page_num += 1
    
    return set


def annoucement_handler(announcement: Announcement):
    id = announcement.id
    url = f"https://www.csindex.com.cn/zh-CN/indices/index-detail/000016#/about/newsDetail?id={id}"
    
    print("Handling ID: ", id)
    driver.get(url)
    
    try:
        # Wait for the page to load and find the element
        import time
        time.sleep(1)
        driver.implicitly_wait(2)
        weditor = driver.find_element(By.CLASS_NAME, "weditor")
        announcement.content = weditor.text

        import re
        
        pattern = re.compile(r"\d{4}.\d+.\d+.")
        match = pattern.search(announcement.content)
        if not match:
            pattern = re.compile(r"\d{4}年\d+月\d+日")
            match = pattern.search(announcement.content)
        if match:
            chinese_date = match.group()
            english_date = chinese_date.replace("年", "-").replace("月", "-").replace("日", "")
            announcement.valid_time = datetime.strptime(english_date, "%Y-%m-%d")

        # Check for PDF link
        file_link = weditor.find_element(By.XPATH, ".//a[contains(@href, '.pdf') or contains(@href, '.xlsx')]")
        if file_link:
            file_url = file_link.get_attribute("href")
            file_suffix = file_url.split(".")[-1]

            def download_file():
                response = requests.get(file_url)
                if response.status_code == 200:
                    with open(f"{id}.{file_suffix}", "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded File: {id}.{file_suffix}")
                    announcement.file_name = f"{id}.{file_suffix}"
                else:
                    print(f"Failed to download File: {file_url}")
            download_file()

            def read_file():
                response = requests.get(file_url)
                if response.status_code == 200:
                    return BytesIO(response.content)
                else:
                    print(f"Failed to download File: {file_url}")
                    return None
            
            file_content = read_file()

            if file_suffix == "pdf":
                pdf_extractor = PDFExtractor(announcement)    
                pdf_extractor.extract_stock_info(file_content)
            elif file_suffix == "xlsx":
                xlsx_extractor = XLSXExtractor(announcement)
                xlsx_extractor.extract_stock_info(file_content)

    except Exception as e:
        print(f"Failed to retrieve data from CSIndex website: {e}")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.date().isoformat()
        return super().default(obj)

def main(name):
    announcement_set = get_announcement(name)
    if announcement_set:
        announcement_json = json.dumps(announcement_set.to_dict(), ensure_ascii=False, indent=4, cls=DateTimeEncoder)
        # save the json file
        with open(f"{name}.json", "w", encoding='utf-8') as f:
            f.write(announcement_json)

if __name__ == "__main__":
    def parse_args():
        import argparse
        parser = argparse.ArgumentParser(description="Fetch and process announcements.")
        parser.add_argument("--name", type=str, required=True, help="Index name to search for announcements.")
        return parser.parse_args()

    args = parse_args()
    main(args.name)
