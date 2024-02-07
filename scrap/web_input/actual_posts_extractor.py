from datetime import datetime
from web_input.page_extractor import PageExtractor
import os

class ActualPostsExtractor:
    def __init__(self, logging):
        self.logging = logging
    
    def load_saved_date(self):
        try:
            with open("storage/saved_date.txt", "r") as file:
                saved_date_iso = file.read().strip()
                saved_date = datetime.fromisoformat(saved_date_iso)
        except Exception as e:
            msg = f"Cannot load saved date, Error: {e}"
            self.logging.error(msg)
            print(msg)
            return None
        
        return saved_date

    def load_sent_urls(self):
        self.sent_urls = []
        try:
            with open("storage/sent_urls.txt", "r") as file:
                self.sent_urls = [line.strip() for line in file]
        except Exception as e:
            self.sent_urls = []
            msg = f"Cannot load sent urls, Error: {e}"
            self.logging.error(msg)
            print(msg)
        return self.sent_urls

    def check_url_already_sent(self, url_to_check):
        return url_to_check in self.sent_urls

    def save_latest_date(self, date):
        date_iso = date.isoformat()
        filename = "storage/saved_date.txt"
        try:
            with open(filename, "w") as file:
                file.write(date_iso)
                os.chmod(filename, 0o666)
        except Exception as e:
            msg = f"Cannot save latest date, Error: {e}"
            self.logging.error(msg)
            print(msg)
            return
        
        msg = f"Saved last article date is: {date}"
        self.logging.info(msg)
        print(msg)

    def update_sent_urls(self, append_url):
        self.sent_urls.append(append_url)
        last_urls = self.sent_urls[-10:]
        filename = "storage/sent_urls.txt"
        try:
            with open(filename, "w") as file:
                file.write('\n'.join(last_urls))
                os.chmod(filename, 0o666)
        except Exception as e:
            msg = f"Cannot update sent urls, Error: {e}"
            self.logging.error(msg)
            print(msg)
        
    def extract(self, html):
        self.load_sent_urls()   # current object state initialization
        saved_date = self.load_saved_date()
        msg = f"Collecting articles starting from date: {saved_date}" if saved_date else "Collecting all articles"
        self.logging.info(msg)
        print(msg)

        page_extractor = PageExtractor(html)
        postDtos = page_extractor.extract_post_dtos_from_page()
        msg = f"Total articles found: {len(postDtos)}"
        self.logging.info(msg)
        print(msg)

        actual_elements = []
        for postDto in postDtos:
            if self.check_url_already_sent(postDto.url):
                msg = f"News with this url {postDto.url} was already sent. Skipping..."
                self.logging.info(msg)
                print(msg)
                continue
            
            if not saved_date or postDto.dt > saved_date:
                actual_elements.append(postDto)

        return actual_elements