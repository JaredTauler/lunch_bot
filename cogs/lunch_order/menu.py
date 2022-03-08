from __main__ import CONFIG

from PIL import Image
from io import BytesIO
import requests
import datetime as dt
import json
import nextcord

class LunchMenu():
    url = CONFIG["lunch-menu"]

    @staticmethod
    def Today(ShowServingSize=False):
        today = dt.datetime.now().date().today()
        get = requests.get(
            LunchMenu.url + today.strftime("%Y/%m/%d")
        )
        x = json.loads(get.text)
        for day in x["days"]:
            if day["date"] == today.strftime("%Y-%m-%d"):
                break

        items = day["menu_items"]

        if not items:  # Looks like lunch isnt being served today.
            return False
        else:
            String = ""
            Drinks = []
            Pictures = []
            for food in items:
                try:
                    f = food.get("food")
                    if f: # Food item
                        img = f.get("image_url")
                        if img:
                            Pictures.append(img)
                        String += f'{f.get("name")}'
                        if ShowServingSize: # Funny that you can show this but seems like useless information.
                            ss = f.get("serving_size_info")
                            if ss:
                                String +=f': {ss["serving_size_amount"]} {ss["serving_size_unit"]}'
                        String += "\n"
                    else: # Drink item
                        Drinks.append(food.get("text"))
                except Exception as e:
                    print(e)
            # They are not consistent with how they log available drinks, so just look for the text "juice".
            x = ""
            for i in Drinks:
                x+=str(i)
            if x.lower().find("juice") != -1:
                String += f"\nJuice is available today.\n"

            return String, CombinePics(Pictures)

def CombinePics(imgs):
    if len(imgs) <= 1:
        return None

    images = []
    for url in imgs:
        response = requests.get(url)
        images.append(Image.open(BytesIO(response.content)))

    widths, heights = zip(*(i.size for i in images))

    total_width = max(widths)
    max_height = sum(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    img_byte_arr = BytesIO()
    new_im.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return nextcord.File(fp=BytesIO(img_byte_arr), filename="tasty_food.png")
