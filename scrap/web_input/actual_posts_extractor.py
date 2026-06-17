from datetime import datetime
from web_input.page_extractor import PageExtractor
from db.storage import ScrapStorage


class ActualPostsExtractor:
    def __init__(self, logging=None):
        self.logging = logging
        self.storage = ScrapStorage(logging=logging)

    def check_url_already_sent(self, url_to_check):
        return self.storage.url_already_sent(url_to_check)

    def update_sent_urls(self, append_url):
        self.storage.mark_url_sent(append_url)

    def save_latest_date(self, date):
        self.storage.save_latest_date(date)
        msg = f"Saved last article date is: {date}"
        if self.logging:
            self.logging.info(msg)
        print(msg)

    def extract(self, html):
        saved_date = self.storage.load_latest_date()
        msg = f"Collecting articles starting from date: {saved_date}" if saved_date else "Collecting all articles"
        if self.logging:
            self.logging.info(msg)
        print(msg)

        page_extractor = PageExtractor(html)
        postDtos = page_extractor.extract_post_dtos_from_page()
        msg = f"Total articles found: {len(postDtos)}"
        if self.logging:
            self.logging.info(msg)
        print(msg)

        actual_elements = []
        for postDto in postDtos:
            if self.check_url_already_sent(postDto.url):
                msg = f"News with this url {postDto.url} was already sent. Skipping..."
                if self.logging:
                    self.logging.info(msg)
                print(msg)
                continue

            if not saved_date or postDto.dt > saved_date:
                actual_elements.append(postDto)

        return actual_elements
