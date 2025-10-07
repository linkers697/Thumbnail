import os
import re
import random
import aiohttp
import aiofiles
import traceback
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def truncate(text):
    words = text.split(" ")
    text1, text2 = "", ""
    for w in words:
        if len(text1) + len(w) < 30:
            text1 += " " + w
        elif len(text2) + len(w) < 30:
            text2 += " " + w
    return [text1.strip(), text2.strip()]


def draw_text_with_outline(draw, pos, text, font, fill, outline_color=(0, 0, 0)):
    x0, y0 = pos
    outline_range = 2
    for dx in range(-outline_range, outline_range + 1):
        for dy in range(-outline_range, outline_range + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x0 + dx, y0 + dy), text, font=font, fill=outline_color)
    draw.text((x0, y0), text, font=font, fill=fill)


async def get_thumb(videoid: str):
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
            duration = result.get("duration", "Unknown Mins")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        icons = Image.open("AloneMusic/assets/icons.png").convert("RGBA")
        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")
        youtube_resized = changeImageSize(1280, 720, youtube)

        # Background: blurred + gradient overlay
        bg = youtube_resized.filter(ImageFilter.GaussianBlur(25))
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.4)
        overlay = Image.new("RGBA", bg.size, (15, 15, 25, 200))
        background = Image.alpha_composite(bg, overlay)

        # Logo crop + glow + shadow
        Xc, Yc = youtube.width / 2, youtube.height / 2
        x1, y1, x2, y2 = Xc - 250, Yc - 250, Xc + 250, Yc + 250
        rand_color = (random.randint(100, 255), random.randint(50, 200), random.randint(100, 255))
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((350, 350), Image.ANTIALIAS)

        glow = ImageOps.expand(logo, border=20, fill=rand_color)
        glow = glow.filter(ImageFilter.GaussianBlur(15))
        background.paste(glow, (80, 120), glow)
        background.paste(logo, (100, 140), logo)

        draw = ImageDraw.Draw(background)
        font_chan = ImageFont.truetype("AloneMusic/assets/font2.ttf", 30)
        font_small = ImageFont.truetype("AloneMusic/assets/font.ttf", 28)
        font_title = ImageFont.truetype("AloneMusic/assets/font3.ttf", 50)

        stitle = truncate(title)
        draw_text_with_outline(draw, (565, 160), stitle[0], font_title, (255, 255, 255))
        if stitle[1]:
            draw_text_with_outline(draw, (565, 220), stitle[1], font_title, (240, 240, 240))

        # channel + views
        draw.text((565, 300), f"{channel} | {views[:23]}", font=font_chan, fill=(200, 200, 200))

        # modern progress bar
        draw.rounded_rectangle([(565, 370), (1130, 390)], radius=10, fill=(50, 50, 50))
        draw.rounded_rectangle([(565, 370), (950, 390)], radius=10, fill=rand_color)
        draw.ellipse([(940, 365), (970, 395)], fill=rand_color)

        # time
        draw.text((565, 400), "00:00", font=font_chan, fill=(255, 255, 255))
        draw.text((1080, 400), duration[:23], font=font_chan, fill=(255, 255, 255))

        # music icons
        icons_resized = icons.resize((560, 58), Image.ANTIALIAS)
        background.paste(icons_resized, (565, 460), icons_resized)

        # small overlay
        small_thumb = youtube.resize((120, 70), Image.ANTIALIAS)
        background.paste(small_thumb, (1080, 30), small_thumb)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        tpath = f"cache/{videoid}.png"
        background.save(tpath)
        return tpath

    except Exception as e:
        traceback.print_exc()
        return None
