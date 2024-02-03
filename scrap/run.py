import requests
from dotenv import load_dotenv
import os
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI

load_dotenv()


def get_page_data(url, cookies, headers):
    response = requests.get(url, cookies=cookies, headers=headers)
    return response


def load_saved_date():
    try:
        with open("saved_date.txt", "r") as file:
            saved_date_iso = file.read().strip()
            saved_date = datetime.fromisoformat(saved_date_iso)
    except:
        return None
    return saved_date


def extract_date(cardlist):
    date_info = cardlist.find("div", class_="meta-info").text.strip()
    date_formatted = date_info.split("Last Updated :")[1].strip()[:-4]
    dt = datetime.strptime(date_formatted, "%b %d %Y | %I:%M %p")
    return dt


def extract_title_and_url(cardlist):
    h = cardlist.find(["h2", "h3", "h4"])
    if not h:
        return None, None
    url = h.a["href"]
    title = h.text.strip()
    return title, url


def extract_elements_from_page(soup):
    elements = []
    cardlists = soup.find_all("div", class_="cardlist")
    for cardlist in cardlists:
        title, url = extract_title_and_url(cardlist)
        if not title:
            continue
        dt = extract_date(cardlist)
        elements.append([title, url, dt])

    sorted_by_date = []
    if elements:
        sorted_by_date = sorted(elements, key=lambda x: x[2])
    return sorted_by_date


def print_elements(sorted_elements):
    for element in sorted_elements:
        print(f"url: {element[0]}, title: {element[1]}, date: {element[2]}")


def save_latest_date(date):
    date_iso = date.isoformat()
    filename = "saved_date.txt"
    with open(filename, "w") as file:
        file.write(date_iso)
        os.chmod(filename, 0o666)
    print("Saved last article date is: ", date)


def send_to_telegram(element):

    apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
    chatID = os.getenv("TELEGRAM_CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"
    headers = {"Content-Type": "application/json"}
    url = element[1]
    hindi = get_hindi_translation(element[0])
    text = f"[{hindi}]({url})"
    print(f"Sending to telegram: {text} of date: {element[2]}")

    try:
        data = {
            "chat_id": chatID,
            "text": text,
            "parse_mode": "Markdown",
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


def main():
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
    url = "https://www.business-standard.com/latest-news"

    response = get_page_data(url, cookies, headers)

    if response.status_code == 200:
        saved_date = load_saved_date()
        if saved_date:
            print(f"Collecting articles starting from date: {saved_date}")
        else:
            print("Collecting all articles")

        soup = BeautifulSoup(response.text, "html.parser")
        elements = extract_elements_from_page(soup)
        print("Total articles found: ", len(elements))

        actual_elements = []
        for element in elements:
            if not saved_date or element[2] > saved_date:
                actual_elements.append(element)

        if not actual_elements:
            print("No new articles found.")
            return
        else:
            print("Found new articles: ", len(actual_elements))

        elements = actual_elements

        for element in actual_elements:
            send_to_telegram(element)

        save_latest_date(element[2])
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


if __name__ == "__main__":
    main()
