from bs4 import BeautifulSoup
import re

class ArticleExtractor():
    def __init__(self, text):
        self.soup = BeautifulSoup(text, "html.parser")

    def extract(self, postDto):
        img = self.extract_image()
        if img:
            print("Image from article list will be replaced: ", postDto.img_url)
            postDto.img_url = img["src"]
            print("Image taken from article: ", postDto.img_url)
        
        postDto.article = self.extract_article()
        # print("Article extracted: ", postDto.article)
        return postDto
    
    def extract_image(self):
        story_image = self.soup.find("div", class_="story-image")
        img = story_image.find("img") if story_image else None
        print("Story image: ", img)
        return img

    def extract_article(self):
        html = self.soup.find("div", class_="MainStory_storycontent__Pe3ys")
        if not html:
            return None
        divs_without_class = html.find_all("div", class_=False)
        article = ""
        for div in divs_without_class:
            paragraph = div.text.strip()
            paragraph = re.sub(r"\s{3,}", "\n\n", paragraph)
            if len(paragraph) > 0:
                article += paragraph + "\n"
        return article
