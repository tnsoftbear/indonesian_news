from datetime import datetime
from dotenv import load_dotenv
from web_input.article_extractor import ArticleExtractor
from web_input.page_extractor import PageExtractor
from translate.hindi_translator import HindiTranslator
from publish.telegram.telegram_publisher import TelegramPublisher
import os
import requests

load_dotenv()

def get_page_data(url):
    cookies = {"_sid": os.getenv("SID")}
    headers = {
        "authority": "www.business-standard.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.7",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }    
    
    response = requests.get(url, cookies=cookies, headers=headers)
    return response


def load_saved_date():
    try:
        with open("storage/saved_date.txt", "r") as file:
            saved_date_iso = file.read().strip()
            saved_date = datetime.fromisoformat(saved_date_iso)
    except:
        return None
    return saved_date

def load_sent_urls():
    urls = []
    try:
        with open("storage/sent_urls.txt", "r") as file:
            urls = [line.strip() for line in file]
    except:
        urls = []
    return urls

def save_latest_date(date):
    date_iso = date.isoformat()
    filename = "storage/saved_date.txt"
    with open(filename, "w") as file:
        file.write(date_iso)
        os.chmod(filename, 0o666)
    print("Saved last article date is: ", date)

def update_sent_urls(sent_urls):
    last_urls = sent_urls[-10:]
    filename = "storage/sent_urls.txt"
    with open(filename, "w") as file:
        file.write('\n'.join(last_urls))
        os.chmod(filename, 0o666)

def check_url_already_sent(url_to_check, sent_urls):
    return url_to_check in sent_urls

def enrich_with_article_data(postDto):
    response = get_page_data(postDto.url)
    if response.status_code == 200:
        article_extractor = ArticleExtractor(response.text)
        postDto = article_extractor.extract(postDto)
    return postDto

def main():
    url = "https://www.business-standard.com/latest-news"

    response = get_page_data(url)

    if response.status_code == 200:
        sent_urls = load_sent_urls()
        saved_date = load_saved_date()
        if saved_date:
            print(f"Collecting articles starting from date: {saved_date}")
        else:
            print("Collecting all articles")

        page_extractor = PageExtractor(response.text)
        postDtos = page_extractor.extract_post_dtos_from_page()
        print("Total articles found: ", len(postDtos))

        actual_elements = []
        for postDto in postDtos:
            if check_url_already_sent(postDto.url, sent_urls):
                print(f"News with this url {postDto.url} was already sent. Skipping...")
                continue
            if not saved_date or postDto.dt > saved_date:
                actual_elements.append(postDto)

        if not actual_elements:
            print("No new articles found.")
            return
        else:
            print("Found new articles: ", len(actual_elements))
            
        apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
        chatID = os.getenv("TELEGRAM_CHAT_ID")
        hindiTranslator = HindiTranslator()
        telegramPublisher = TelegramPublisher(apiToken, chatID, hindiTranslator)
        for index, postDto in enumerate(actual_elements):
            # if index % 2 == 0:
            postDto = enrich_with_article_data(postDto)
            telegramPublisher.send_photo_to_telegram(postDto)
            # send_message_with_image_to_telegram(postDto)
            sent_urls.append(postDto.url)
            update_sent_urls(sent_urls)
            # else:
            #     send_message_to_telegram(postDto)
            break

        save_latest_date(postDto.dt)
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


if __name__ == "__main__":
    main()
