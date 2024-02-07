from datetime import datetime
from dto.post_dto import PostDto
from bs4 import BeautifulSoup

class PageExtractor:
    def __init__(self, text):
        self.soup = BeautifulSoup(text, "html.parser")

    def extract_date(self, cardlist):
        meta_info = cardlist.find("div", class_="MetaPost_metainfo__MmNP0")
        date_info = meta_info.text.strip()
        date_formatted = date_info.split("Last Updated :")[1].strip()[:-4]
        dt = datetime.strptime(date_formatted, "%b %d %Y | %I:%M %p")
        return dt

    def extract_title_and_url(self, cardlist):
        h = cardlist.find(["h2", "h3", "h4"])
        if not h:
            return None, None
        url = h.a["href"]
        title = h.text.strip()
        return title, url
    
    def extract_image_url(self, cardlist):
        img = cardlist.find("img")
        src = None
        if img:
            # url содержит параметры размеров картинки (100,100), убирая которые мы получаем оригинал
            src = img["src"].split('?')[0]
        
        return src

    def extract_post_dtos_from_page(self):
        postDtos = []
        cardlists = self.soup.find_all("div", class_="cardlist")
        for cardlist in cardlists:
            title, url = self.extract_title_and_url(cardlist)
            if not title:
                continue
            
            dt = self.extract_date(cardlist)
            img_url = self.extract_image_url(cardlist)
            dto = PostDto(title=title, url=url, dt=dt, img_url=img_url, article=None)
            postDtos.append(dto)

        sorted_by_date = []
        if postDtos:
            sorted_by_date = sorted(postDtos, key=lambda x: x.dt)
        return sorted_by_date
