import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from openai import OpenAI
import re
from web_input.page_extractor import PageExtractor
from web_input.article_extractor import ArticleExtractor

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

def send_message_to_telegram(postDto):

    apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
    chatID = os.getenv("TELEGRAM_CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"
    headers = {"Content-Type": "application/json"}
    url = postDto.url
    hindi = get_hindi_translation(postDto.title)
    text = f"<a href=\"{url}\">{hindi}</a>"
    print(f"Sending to telegram: {text} of date: {postDto.dt}")

    try:
        data = {
            "chat_id": chatID,
            "text": text,
            "parse_mode": "HTML",
        }
        response = requests.post(apiURL, json=data, headers=headers)
    except Exception as e:
        print(e)

def send_message_with_image_to_telegram(postDto):

    apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
    chatID = os.getenv("TELEGRAM_CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"
    headers = {"Content-Type": "application/json"}
    url = postDto.url
    limit = 4092
    article = postDto.article[:limit] if postDto.article is not None else ""
    text = f'{postDto.title}\n\n{article}'
    # limit = 1024 - len(postDto.img_url) - 7;
    print(text)
    hindi = get_hindi_translation_limited2(text, limit)
    text = f"[ ]({postDto.img_url} {hindi}"
    print(f"Sending to telegram: {text} of date: {postDto.dt}")

    try:
        data = {
            "chat_id": chatID,
            "text": text,
            "parse_mode": "Markdown",
        }
        response = requests.post(apiURL, json=data, headers=headers)
        print(response)
        print(response.content)
    except Exception as e:
        print(e)
       
def send_photo_to_telegram(postDto):
    apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
    chatID = os.getenv("TELEGRAM_CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendPhoto"
    headers = {"Content-Type": "application/json"}
    caption = f"<a href=\"{postDto.url}\">{postDto.title}</a>"
    if postDto.article:
        caption += "\n\n" + postDto.article[:1024]

    desired_length = 1024
    caption = get_hindi_translation_limited(caption, desired_length)
    if len(caption) > desired_length:
        desired_length -= 4
        caption = caption[:desired_length]
        caption = re.sub(r'\s[^\s]*$', '', caption) + " ..."
    
    print(f"Sending to telegram: {caption} of date: {postDto.dt}")

    try:
        data = {
            "chat_id": chatID,
            "photo": postDto.img_url,
            "caption": caption,
            "parse_mode": "HTML",
        }
        response = requests.post(apiURL, json=data, headers=headers)
    except Exception as e:
        print(e)

def get_hindi_translation(original):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    content = f"Return translation to Hindi '{original}'"

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content}
        ],
    )

    hindi_translation = chat_completion.choices[0].message.content
    return hindi_translation

def get_hindi_translation_limited(original, limit):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    content = f"Return translation to Hindi. Do not exceed {limit} characters. Keep link in the beginning: '{original}'"

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content}
        ],
    )

    hindi_translation = chat_completion.choices[0].message.content
    return hindi_translation


def get_hindi_translation_limited2(original, limit):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    content = f"Formulate text to be an article. Return translation to Hindi. Do not exceed {limit} characters. Keep Markdown format: '{original}'"

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content}
        ],
    )

    hindi_translation = chat_completion.choices[0].message.content
    return hindi_translation

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

        for index, postDto in enumerate(actual_elements):
            # if index % 2 == 0:
            postDto = enrich_with_article_data(postDto)
            send_photo_to_telegram(postDto)
            # send_message_with_image_to_telegram(postDto)
            sent_urls.append(postDto.url)
            update_sent_urls(sent_urls)
            # else:
            #     send_message_to_telegram(element)
            break

        save_latest_date(postDto.dt)
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


if __name__ == "__main__":
    main()
