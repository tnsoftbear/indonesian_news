from dotenv import load_dotenv
from generate.image.dalle_image_generator import DalleImageGenerator
from publish.telegram.telegram_publisher import TelegramPublisher
from translate.hindi_translator import HindiTranslator
from web_input.actual_posts_extractor import ActualPostsExtractor
from web_input.article_extractor import ArticleExtractor
from web_input.page_reader import PageReader
from web_input.session_manager import SessionManager
import logging
import os

load_dotenv()

def enrich_with_article_data(postDto, session_manager):
    html_content = session_manager.get_page_content(postDto.url)
    if html_content:
        article_extractor = ArticleExtractor(html_content)
        postDto = article_extractor.extract(postDto)
    return postDto

def read_latest_news(session_manager, actualPostsExtractor):
    url = "https://www.business-standard.com/latest-news"
    html_content = session_manager.get_page_content(url)
    if html_content:
        # Собираем заголовки новостей и дату со страницы latest_news, отфильтровываем обработанные
        actual_posts = actualPostsExtractor.extract(html_content)
        return actual_posts
    
    msg = f"Failed to fetch the page."
    logging.warning(msg)
    print(msg)
    return None

def main():
    os.makedirs("storage", exist_ok=True)
    logging.basicConfig(filename='storage/scrap.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s %(message)s')
    
    # Use automated session manager to handle cookie consent automatically
    msg = "Initializing browser session for automated cookie handling..."
    logging.info(msg)
    print(msg)
    
    session_manager = SessionManager(headless=True)
    sid = session_manager.initialize()
    
    if not sid:
        msg = "Failed to obtain session cookie. Scraping may not work correctly."
        logging.warning(msg)
        print(msg)
        # Continue anyway - some pages may still be accessible
    
    actualPostsExtractor = ActualPostsExtractor(logging)
    actual_posts = read_latest_news(session_manager, actualPostsExtractor)

    if not actual_posts:
        msg = "No new articles found."
        logging.info(msg)
        print(msg)
        session_manager.close()
        return
    
    msg = f"Found new articles: {len(actual_posts)}"
    logging.info(msg)
    print(msg)

    apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
    chatID = os.getenv("TELEGRAM_CHAT_ID")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    hindiTranslator = HindiTranslator(openai_api_key, base_url=openai_base_url)
    imageGenerator = DalleImageGenerator(openai_api_key, base_url=openai_base_url)
    telegramPublisher = TelegramPublisher(apiToken, chatID, logging, hindiTranslator, imageGenerator)
    
    postDto = None
    for index, postDto in enumerate(actual_posts):
        postDto = enrich_with_article_data(postDto, session_manager) # добавить содержимое статьи
        # telegramPublisher.send_photo_to_telegram(postDto)
        # telegramPublisher.send_file_photo_to_telegram(postDto)
        # telegramPublisher.send_generated_photo_to_telegram(postDto)
        # telegramPublisher.send_photo_to_telegram_with_link(postDto)
        telegramPublisher.send_message_with_image_to_telegram(postDto)
        # telegramPublisher.send_message_to_telegram(postDto)
        actualPostsExtractor.update_sent_urls(postDto.url)
        break
    
    if postDto:
        actualPostsExtractor.save_latest_date(postDto.dt)
    
    session_manager.close()


if __name__ == "__main__":
    main()
