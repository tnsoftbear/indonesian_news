from dotenv import load_dotenv
from web_input.article_extractor import ArticleExtractor
from web_input.actual_posts_extractor import ActualPostsExtractor
from translate.hindi_translator import HindiTranslator
from generate.image.dalle_image_generator import DalleImageGenerator
from publish.telegram.telegram_publisher import TelegramPublisher
import os
import requests
import logging

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

def enrich_with_article_data(postDto):
    response = get_page_data(postDto.url)
    if response.status_code == 200:
        article_extractor = ArticleExtractor(response.text)
        postDto = article_extractor.extract(postDto)
    return postDto

def main():
    logging.basicConfig(filename='storage/scrap.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s %(message)s')
    url = "https://www.business-standard.com/latest-news"
    response = get_page_data(url)

    if response.status_code == 200:
        actualPostsExtractor = ActualPostsExtractor(logging)
        # Собираем заголовки новостей и дату со страницы latest_news, отфильтровываем обработанные
        actual_posts = actualPostsExtractor.extract(response.text)
        if not actual_posts:
            msg = "No new articles found."
            logging.info(msg)
            print(msg)
            return
        
        msg = f"Found new articles: {len(actual_posts)}"
        logging.info(msg)
        print(msg)

        apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
        chatID = os.getenv("TELEGRAM_CHAT_ID")
        hindiTranslator = HindiTranslator(os.getenv("OPENAI_API_KEY"))
        imageGenerator = DalleImageGenerator(os.getenv("OPENAI_API_KEY"))
        telegramPublisher = TelegramPublisher(apiToken, chatID, logging, hindiTranslator, imageGenerator)
        for index, postDto in enumerate(actual_posts):
            postDto = enrich_with_article_data(postDto) # добавить содержимое статьи
            # telegramPublisher.send_photo_to_telegram(postDto)
            # telegramPublisher.send_file_photo_to_telegram(postDto)
            # telegramPublisher.send_generated_photo_to_telegram(postDto)
            # telegramPublisher.send_photo_to_telegram_with_link(postDto)
            telegramPublisher.send_message_with_image_to_telegram(postDto)
            # telegramPublisher.send_message_to_telegram(postDto)
            actualPostsExtractor.update_sent_urls(postDto.url)
            break

        actualPostsExtractor.save_latest_date(postDto.dt)
    else:
        msg = f"Failed to fetch the page. Status code: {response.status_code}"
        logging.warning(msg)
        print(msg)


if __name__ == "__main__":
    main()
