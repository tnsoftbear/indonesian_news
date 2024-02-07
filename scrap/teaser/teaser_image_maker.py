import requests
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageFont, ImageDraw
import textwrap

# TODO: complete image processing
class TeaserImageMaker:
    SOURCE = "Source Source Source Source Source Source Source Source"
    def make(self, postDto):
        img_file = 'out.png'
        img_bytes = requests.get(postDto.img_url, stream=True).raw
        img = Image.open(img_bytes)
        print(f"Img, w: {img.size[0]}, h: {img.size[1]}")
        # input_img = img.convert("RGBA")
        # if input_img.mode != 'RGBA':
        #     input_img = input_img.convert('RGBA')
        # width, height = input_img.size
        # alpha_gradient = Image.new('L', (1, height), color=0xFF)
        # gradient = 4.
        # initial_opacity = 1.
        # 
        # for x, x1 in zip(range(height)[::-1], range(height)):
        #     a = int((initial_opacity * 255.) * 1. - gradient * float(x) / height)
        #     if a > 0:
        #         alpha_gradient.putpixel((0, x1), a)
        #     else:
        #         alpha_gradient.putpixel((0, x1), 0)
        # alpha = alpha_gradient.resize(input_img.size)
        
        # gradient_color = '#182419'
        # line_color = '#1fb6b6'
        # main_color = '#fff'
        # black_img = Image.new('RGBA', (width, height), color=gradient_color)
        # black_img.putalpha(alpha)
        # output_img = Image.alpha_composite(input_img, black_img)
        # font_size = 0.075 if width < height else 0.055
        # font_path = str('resources/font/Devnew.ttf')
        # title_font = ImageFont.truetype(font_path, int(img.size[0] * (font_size - 0.01)))
        # fnt_mir = ImageFont.truetype(font_path, int(img.size[0] * (font_size - 0.02)))
        # info_font = ImageFont.truetype(font_path, int(img.size[0] * (font_size - 0.035)))
        
        # title = "Some title Some title Some title Some title Some title Some title"
        # # title = self.hindiTranslator.get_hindi_translation_limited(postDto.title, 100)
        # # print("Hindi translated title for image:", title)
        # total_text_height, wrapped_text, padding = self._wrap_text_and_get_total_height(
        #     image=img,
        #     text=title,
        #     title_font=title_font,
        #     source_font=info_font
        # )
        # print(f"Total text height: {total_text_height}, wrapped_text: {wrapped_text}, padding: {padding}")
        
        # new_image_height = int(img.size[1] + total_text_height)
        # overlay = Image.new('RGBA', (img.size[0], new_image_height), gradient_color)
        # overlay.paste(output_img, (0, 0))
        
        # img = overlay
        # idraw = ImageDraw.Draw(img)
        
        # width_source = idraw.textlength(self.SOURCE, font=fnt_mir)
        # height_source = fnt_mir.getbbox(self.SOURCE)[-1] + padding
        # txt_height = new_image_height - total_text_height - height_source
        # idraw.text(((img.size[0] - width_source) / 2, txt_height), self.SOURCE, font=fnt_mir,
        #     fill=line_color)

        # current_h = new_image_height - total_text_height

        # for line in wrapped_text:
        #     w = idraw.textlength(line, font=title_font)
        #     h = title_font.getbbox(line)[-1]
        #     idraw.text(((img.size[0] - w) / 2, current_h), line, font=title_font,
        #         fill=main_color)
        #     current_h += h + padding

        # top = (15, txt_height * 1.03)
        # x = (width // 2) - width_source
        # left = (x, txt_height * 1.03)

        # x1 = x + width_source * 2
        # top1 = (x1, txt_height * 1.03)
        # left1 = (width - 15, txt_height * 1.03)

        # top2 = (15, img.size[1] - 10)
        # left2 = (width - 15, new_image_height - 10)

        # idraw.line([top, left], fill=line_color, width=3)
        # idraw.line([top1, left1], fill=line_color, width=3)
        # idraw.line([top2, left2], fill=line_color, width=3)

        path_out = 'storage/' + img_file
        # print("Absolute path:", path_out.absolute())
        print("Result image path:", path_out)
        img.save(path_out, 'PNG')
        return path_out
        # except:
        #     print("Failed to create image")
        #     pass
        
        
    def _wrap_text_and_get_total_height(
            self,
            image: Image,
            text: str,
            title_font: ImageFont.FreeTypeFont,
            source_font: ImageFont.FreeTypeFont
    ) -> Tuple[int, List[str], int]:
        avg_symbol_length = title_font.getlength(text) // len(text)
        width_line = image.size[0] * 0.9
        wrap_width = width_line // avg_symbol_length
        padding = image.size[1] * 0.01

        wrapped_text = textwrap.wrap(text, width=wrap_width)

        total_height = 0
        for line in wrapped_text:
            h = title_font.getbbox(line)[-1]
            total_height += h + padding

        info_height = source_font.getbbox(self.SOURCE)[-1]
        total_height += info_height

        return total_height, wrapped_text, padding        
        
