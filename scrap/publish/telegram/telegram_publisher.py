import requests
import re
from teaser.teaser_image_maker import TeaserImageMaker
from telebot import TeleBot

class TelegramPublisher:
    SOURCE="New Times Telegram"
    
    def __init__(self, botToken, chatID, logging, hindiTranslator, imageGenerator):
        self.chatID = chatID
        self.botToken = botToken
        self.apiUrlBase = f"https://api.telegram.org/bot{botToken}"
        self.logging = logging
        self.hindiTranslator = hindiTranslator
        self.imageGenerator = imageGenerator

    def send_message_to_telegram(self, postDto):
        hindi = self.hindiTranslator.get_hindi_translation(postDto.title)
        text = f"<a href=\"{postDto.url}\">{hindi}</a>"
        self.send_message(text)

    def send_message_with_image_to_telegram(self, postDto, input_limit=4092, output_limit=1024):
        article = postDto.article[:input_limit] if postDto.article is not None else ""
        original_text = f'**{postDto.title}**\n\n{article}'
        print(f"ORIGINAL TEXT: {original_text}")
        if postDto.img_url:
            output_limit -= len(postDto.img_url) - 6;
        hindi = self.hindiTranslator.get_hindi_translation_keep_markdown(original_text, output_limit)
        if postDto.img_url:
            text = f"[ ]({postDto.img_url}) {hindi}"
        else:
            text = f"{hindi}"
        print(f"SENDING TO TELEGRAM: {text}")
        print("Length: ", len(text))
        self.send_message(text, "Markdown")
    
    def send_photo_to_telegram(self, postDto, input_length=2048):
        caption = f"<b>{postDto.title}</b>"
        if postDto.article:
            caption += "\n\n" + postDto.article[:input_length]
        output_length = 1024
        caption = self.hindiTranslator.get_hindi_translation_limited(caption, output_length)
        caption = self.adjust_length(caption, output_length)
        self.send_photo(caption, postDto)
    
    def send_file_photo_to_telegram(self, postDto, input_length=2048):
        if postDto.img_url:
            teaserImageMaker = TeaserImageMaker()
            postDto.img_file = teaserImageMaker.make(postDto)
        
        caption = ""
        if postDto.article:
            caption = "\n\n" + postDto.article[:input_length]
        output_length = 1024
        if caption:
            # caption = self.hindiTranslator.get_hindi_translation_limited(caption, output_length)
            caption = self.adjust_length(caption, output_length)
        
        bot = TeleBot(
            token=self.botToken,
            parse_mode='html',
            disable_web_page_preview=True
        )
        bot.send_photo(
            chat_id=self.chatID,
            photo=open(postDto.img_file, 'rb'),
            caption=caption
        )
        print("News file photo sent to Telegram")
        #self.send_photo(caption, postDto, False)
        
        
    def send_generated_photo_to_telegram(self, postDto, input_length=2048):
        input_caption = f"<b>{postDto.title}</b>"
        if postDto.article:
            input_caption += "\n\n" + postDto.article[:input_length]
        output_length = 1024
        hindi_caption = self.hindiTranslator.get_hindi_translation_limited(input_caption, output_length)
        hindi_caption = self.adjust_length(hindi_caption, output_length)
        
        generated_img_url = self.imageGenerator.generate(input_caption)
        if generated_img_url:
            msg = f"Successfully generated image url: {generated_img_url}"
            self.logging.info(msg)
            print(msg)
            postDto.img_url = generated_img_url
        else:
            msg = "Failed to generate image, original image will be used"
            self.logging.error(msg)
            print(msg)
        
        self.send_photo(hindi_caption, postDto)
        
    def send_photo_to_telegram_with_link(self, postDto, input_length=2048):
        caption = f"<a href=\"{postDto.url}\">{postDto.title}</a>"
        if postDto.article:
            caption += "\n\n" + postDto.article[:input_length]
        output_length = 1024
        caption = self.hindiTranslator.get_hindi_translation_limited_keep_link(caption, output_length)
        caption = self.adjust_length(caption, output_length, True)
        self.send_photo(caption, postDto)
        
    def adjust_length(self, caption, desired_length, is_tail_dots=False):
        if len(caption) > desired_length:
            tail_dots = " ..."
            if is_tail_dots:
                desired_length -= len(tail_dots)
            caption = caption[:desired_length]
            caption = re.sub(r'\s[^\s]*$', '', caption)
            if is_tail_dots:
                caption += tail_dots
        return caption
        
    def send_photo(self, caption, postDto, parse_mode="HTML", is_url=True):
        msg = f"Sending to telegram: {caption} of date: {postDto.dt}"
        self.logging.info(msg)
        print(msg)

        apiURL = f"{self.apiUrlBase}/sendPhoto"
        headers = {"Content-Type": "application/json"}
        if is_url:
            photo = postDto.img_url
        else:
            photo = open(postDto.img_file, 'rb')
        data = {
            "chat_id": self.chatID,
            "photo": photo,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        try:
            response = requests.post(apiURL, json=data, headers=headers)
            msg = f"Response status: {response.status_code}\nResponse content: {response.content}"
            self.logging.debug(msg)
            print(msg)
        except Exception as e:
            msg = f"Cannot send photo to telegram, Error: {e}"
            self.logging.error(msg)
            print(msg)
            
    def send_message(self, text, parse_mode="HTML"):
        apiURL = f"{self.apiUrlBase}/sendMessage"
        headers = {"Content-Type": "application/json"}
        data = {
            "chat_id": self.chatID,
            "text": text,
            "parse_mode": parse_mode,
        }
        try:
            response = requests.post(apiURL, json=data, headers=headers)
            msg = f"Response status: {response.status_code}\nResponse content: {response.content}"
            self.logging.debug(msg)
            print(msg)
        except Exception as e:
            msg = f"Cannot send message to telegram, Error: {e}"
            self.logging.error(msg)
            print(msg)
            