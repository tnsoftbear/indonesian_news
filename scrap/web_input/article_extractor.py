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
        # Try multiple selectors for article image
        img = None
        
        # 1. Original selector
        story_image = self.soup.find("div", class_="story-image")
        if story_image:
            img = story_image.find("img")
        
        # 2. Fallback: og:image meta tag
        if not img:
            og_image = self.soup.find("meta", attrs={"property": "og:image"})
            if og_image and og_image.get("content"):
                img = {"src": og_image["content"]}
                print(f"Image from og:image: {img['src']}")
                return img
        
        # 3. Fallback: first img in article content
        if not img:
            first_img = self.soup.find("img")
            if first_img and first_img.get("src"):
                img = {"src": first_img["src"]}
                print(f"Image from first <img>: {img['src']}")
                return img
        
        print("Story image: ", img)
        return img

    def extract_article(self):
        html = self.soup.find("div", class_="MainStory_storycontent__Pe3ys")
        
        # Fallback: try article tag or main content div
        if not html:
            html = self.soup.find("article")
        
        if not html:
            html = self.soup.find("div", attrs={"itemprop": "articleBody"})
        
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
