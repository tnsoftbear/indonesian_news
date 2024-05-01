from dotenv import load_dotenv
from generate.image.dalle_image_generator import DalleImageGenerator
from publish.telegram.telegram_publisher import TelegramPublisher
from translate.hindi_translator import HindiTranslator
from web_input.actual_posts_extractor import ActualPostsExtractor
from web_input.article_extractor import ArticleExtractor
from web_input.page_reader import PageReader
import logging
import os

load_dotenv()

def enrich_with_article_data(postDto, sid):
    response = PageReader.get_page_data(postDto.url, sid)
    if response.status_code == 200:
        article_extractor = ArticleExtractor(response.text)
        postDto = article_extractor.extract(postDto)
    return postDto

def read_latest_news(sid, actualPostsExtractor):
    url = "https://www.business-standard.com/latest-news"
    response = PageReader.get_page_data(url, sid)
    if response.status_code == 200:
        # Собираем заголовки новостей и дату со страницы latest_news, отфильтровываем обработанные
        actual_posts = actualPostsExtractor.extract(response.text)
        return actual_posts
    
    msg = f"Failed to fetch the page. Status code: {response.status_code}"
    logging.warning(msg)
    print(msg)
    return None

def main():
    sid = os.getenv("SID")
    logging.basicConfig(filename='storage/scrap.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s %(message)s')
    actualPostsExtractor = ActualPostsExtractor(logging)
    actual_posts = read_latest_news(sid, actualPostsExtractor)

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
        postDto = enrich_with_article_data(postDto, sid) # добавить содержимое статьи
        # telegramPublisher.send_photo_to_telegram(postDto)
        # telegramPublisher.send_file_photo_to_telegram(postDto)
        # telegramPublisher.send_generated_photo_to_telegram(postDto)
        # telegramPublisher.send_photo_to_telegram_with_link(postDto)
        telegramPublisher.send_message_with_image_to_telegram(postDto)
        # telegramPublisher.send_message_to_telegram(postDto)
        actualPostsExtractor.update_sent_urls(postDto.url)
        break

    actualPostsExtractor.save_latest_date(postDto.dt)


if __name__ == "__main__":
    main()
