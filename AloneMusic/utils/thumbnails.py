import os
import re
import random
import aiohttp
import aiofiles
import traceback
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch

DEFAULT_IMAGE = "AloneMusic/assets/default.png"

def changeImageSize(maxWidth, maxHeight, image):
    try:
        widthRatio = maxWidth / image.size[0]
        heightRatio = maxHeight / image.size[1]
        newWidth = int(widthRatio * image.size[0])
        newHeight = int(heightRatio * image.size[1])
        newImage = image.resize((newWidth, newHeight))
        return newImage
    except Exception:
        return image

def truncate(text):
    try:
        list = text.split(" ")
        text1, text2 = "", ""
        for i in list:
            if len(text1) + len(i) < 30:
                text1 += " " + i
            elif len(text2) + len(i) < 30:
                text2 += " " + i
        return [text1.strip(), text2.strip()]
    except Exception:
        return ["Title", ""]

async def get_thumb(videoid: str):
    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0] if (await results.next())["result"] else {}

        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
        thumbnail_url = result.get("thumbnails", [{"url": DEFAULT_IMAGE}])[0].get("url", DEFAULT_IMAGE).split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()
                else:
                    # fallback image
                    thumbnail_url = DEFAULT_IMAGE

        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
        except Exception:
            youtube = Image.open(DEFAULT_IMAGE)

        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(ImageFilter.GaussianBlur(20))
        background = ImageEnhance.Brightness(background).enhance(0.6)

        # Logo crop with safety
        Xcenter, Ycenter = youtube.width / 2, youtube.height / 2
        x1, y1 = Xcenter - 250, Ycenter - 250
        x2, y2 = Xcenter + 250, Ycenter + 250

        rand_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        logo = youtube.crop((x1, y1, x2, y2)) if hasattr(youtube, "crop") else youtube
        logo.thumbnail((370, 370), Image.ANTIALIAS)
        logo = ImageOps.expand(logo, border=17, fill=rand_color)
        background.paste(logo, (100, 150), logo if logo.mode == "RGBA" else None)

        # Draw text
        draw = ImageDraw.Draw(background)
        try:
            arial = ImageFont.truetype("AloneMusic/assets/font2.ttf", 30)
            font = ImageFont.truetype("AloneMusic/assets/font.ttf", 30)
            tfont = ImageFont.truetype("AloneMusic/assets/font3.ttf", 45)
        except Exception:
            arial = font = tfont = ImageFont.load_default()

        stitle = truncate(title)
        draw.text((565, 180), stitle[0], (255, 255, 255), font=tfont)
        draw.text((565, 230), stitle[1], (255, 255, 255), font=tfont)
        draw.text((565, 320), f"{channel} | {views[:23]}", (255, 255, 255), font=arial)

        draw.line([(565, 385), (1130, 385)], fill="white", width=8, joint="curve")
        draw.line([(565, 385), (999, 385)], fill=rand_color, width=8, joint="curve")
        draw.ellipse([(999, 375), (1020, 395)], outline=rand_color, fill=rand_color, width=15)
        draw.text((565, 400), "00:00", (255, 255, 255), font=arial)
        draw.text((1080, 400), f"{duration[:23]}", (255, 255, 255), font=arial)

        # Paste icons safely
        try:
            icons = Image.open("AloneMusic/assets/icons.png").resize((580, 62))
            background.paste(icons, (565, 450), icons if icons.mode == "RGBA" else None)
        except Exception:
            pass

        # Remove temp thumbnail
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except Exception:
            pass

        tpath = f"cache/{videoid}.png"
        background.save(tpath)
        return tpath

    except Exception:
        traceback.print_exc()
        return None
