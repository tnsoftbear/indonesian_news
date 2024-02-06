import requests
import re

class TelegramPublisher:
    
    def __init__(self, botToken, chatID, hindiTranslator):
        self.chatID = chatID
        self.apiUrlBase = f"https://api.telegram.org/bot{botToken}"
        self.hindiTranslator = hindiTranslator

    def send_message_to_telegram(self, postDto):

        apiURL = f"{self.apiUrlBase}/sendMessage"
        headers = {"Content-Type": "application/json"}
        url = postDto.url
        hindi = self.hindiTranslator.get_hindi_translation(postDto.title)
        text = f"<a href=\"{url}\">{hindi}</a>"
        print(f"Sending to telegram: {text} of date: {postDto.dt}")

        try:
            data = {
                "chat_id": self.chatID,
                "text": text,
                "parse_mode": "HTML",
            }
            response = requests.post(apiURL, json=data, headers=headers)
        except Exception as e:
            print(e)

    def send_message_with_image_to_telegram(self, postDto):
        apiURL = f"{self.apiUrlBase}/sendMessage"
        headers = {"Content-Type": "application/json"}
        limit = 4092
        article = postDto.article[:limit] if postDto.article is not None else ""
        text = f'{postDto.title}\n\n{article}'
        # limit = 1024 - len(postDto.img_url) - 7;
        print(text)
        hindi = self.hindiTranslator.get_hindi_translation_keep_markdown(text, limit)
        text = f"[ ]({postDto.img_url} {hindi}"
        print(f"Sending to telegram: {text} of date: {postDto.dt}")

        try:
            data = {
                "chat_id": self.chatID,
                "text": text,
                "parse_mode": "Markdown",
            }
            response = requests.post(apiURL, json=data, headers=headers)
            print(response)
            print(response.content)
        except Exception as e:
            print(e)
        
    def send_photo_to_telegram(self, postDto):
        apiURL = f"{self.apiUrlBase}/sendPhoto"
        headers = {"Content-Type": "application/json"}
        caption = f"<a href=\"{postDto.url}\">{postDto.title}</a>"
        if postDto.article:
            caption += "\n\n" + postDto.article[:1024]

        desired_length = 1024
        caption = self.hindiTranslator.get_hindi_translation_limited(caption, desired_length)
        if len(caption) > desired_length:
            desired_length -= 4
            caption = caption[:desired_length]
            caption = re.sub(r'\s[^\s]*$', '', caption) + " ..."
        
        print(f"Sending to telegram: {caption} of date: {postDto.dt}")

        try:
            data = {
                "chat_id": self.chatID,
                "photo": postDto.img_url,
                "caption": caption,
                "parse_mode": "HTML",
            }
            response = requests.post(apiURL, json=data, headers=headers)
        except Exception as e:
            print(e)