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
    except FileNotFoundError:
        saved_date_iso = None
    return saved_date_iso

def parse_date_string(date_string):
    date_format = "%b %d %Y | %I:%M %p"
    date_object = datetime.strptime(date_string, date_format)
    return date_object

def extract_elements_from_page(soup, h_tags):
    elements = []
    cardlists = soup.find_all('div', class_='cardlist')
    for cardlist in cardlists:
        h = None
        for tag in h_tags:
            h = cardlist.find(tag)
            if h:
                break
        if h:
            h_a_href = h.a['href']
            h_value = h.text.strip()
            meta_info_value = cardlist.find('div', class_='meta-info').text.strip()
            date_string = meta_info_value.split("Last Updated :")[1].strip()[:-4]
            date_object = parse_date_string(date_string)
            elements.append([h_value, h_a_href, date_object])
            
    sorted_elements = []    
    if elements:
        sorted_elements = sorted(elements, key=lambda x: x[2])
    return sorted_elements

def print_elements(sorted_elements):
    for element in sorted_elements:
        print(f"h_a_href: {element[0]}, h_value: {element[1]}, date_object: {element[2]}")

def save_latest_date(saved_date):
    saved_date_iso = saved_date.isoformat()
    filename = "saved_date.txt"
    with open(filename, "w") as file:
        file.write(saved_date_iso)
        os.chmod(filename, 0o666)
    print("Saved last article date is: ", saved_date)

# -----------

def send_to_telegram(element):

    apiToken = os.getenv("TELEGRAM_BOT_TOKEN")
    chatID = os.getenv('TELEGRAM_CHAT_ID')
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    headers = {'Content-Type': 'application/json'}
    url = element[1]
    hindi = get_hindi_translation(element[0])
    text = f'[{hindi}]({url})'
    print(f'Sending to telegram: {text} of date: {element[2]}')

    try:
        data = {
            'chat_id': chatID,
            'text': text,
            'parse_mode': 'Markdown',
        }
        response = requests.post(apiURL, json=data, headers=headers)
    except Exception as e:
        print(e)

def get_hindi_translation(original):
    # Set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)

    # Create a chat completion
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Translate to Hindi '{original}'. Return only Hindi text."}
        ]
    )

    # Extract and return the Hindi text from the response
    hindi_translation = chat_completion.choices[0].message.content
    return hindi_translation

def main():
    cookies = {'_sid': os.getenv("SID")}
    headers = {
        'authority': 'www.business-standard.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.7',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    url = "https://www.business-standard.com/latest-news"

    response = get_page_data(url, cookies, headers)

    if response.status_code == 200:
        saved_date_iso = load_saved_date()
        saved_date = datetime.fromisoformat(saved_date_iso) if saved_date_iso else None
        if saved_date:
            print(f'Collecting articles starting from date: {saved_date}')
        else:
            print('Collecting all articles')

        soup = BeautifulSoup(response.text, 'html.parser')
        h_tags = ['h2', 'h3', 'h4']
        elements = extract_elements_from_page(soup, h_tags)
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
            
        save_latest_date(actual_elements[-1][2])
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

if __name__ == "__main__":
    main()