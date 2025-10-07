import os
import re
import random
import aiohttp
import aiofiles
import traceback
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageSequence
from youtubesearchpython.__future__ import VideosSearch

DEFAULT_IMAGE = "AloneMusic/assets/default.png"

def changeImageSize(maxWidth, maxHeight, image):
    try:
        widthRatio = maxWidth / image.size[0]
        heightRatio = maxHeight / image.size[1]
        newWidth = int(widthRatio * image.size[0])
        newHeight = int(heightRatio * image.size[1])
        return image.resize((newWidth, newHeight))
    except Exception:
        return image

def truncate(text):
    try:
        words = text.split(" ")
        text1, text2 = "", ""
        for i in words:
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
        result_data = await results.next()
        result = result_data["result"][0] if result_data.get("result") else {}

        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
        thumbnail_url = result.get("thumbnails", [{"url": DEFAULT_IMAGE}])[0].get("url", DEFAULT_IMAGE).split("?")[0]

        # Fetch thumbnail image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())
                else:
                    thumbnail_url = DEFAULT_IMAGE

        # Open image safely
        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
        except Exception:
            youtube = Image.open(DEFAULT_IMAGE)

        image1 = changeImageSize(1280, 720, youtube)
        background = image1.convert("RGBA").filter(ImageFilter.GaussianBlur(20))
        background = ImageEnhance.Brightness(background).enhance(0.6)

        # Crop and paste logo safely
        Xc, Yc = youtube.width / 2, youtube.height / 2
        x1, y1 = Xc - 250, Yc - 250
        x2, y2 = Xc + 250, Yc + 250
        rand_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        logo = youtube.crop((x1, y1, x2, y2)) if hasattr(youtube, "crop") else youtube
        logo.thumbnail((370, 370), Image.ANTIALIAS)
        logo = ImageOps.expand(logo, border=17, fill=rand_color)
        background.paste(logo, (100, 150), logo if logo.mode == "RGBA" else None)

        # Draw text
        draw = ImageDraw.Draw(background)
        try:
            arial = ImageFont.truetype("AloneMusic/assets/font2.ttf", 30)
            tfont = ImageFont.truetype("AloneMusic/assets/font3.ttf", 45)
        except Exception:
            arial = tfont = ImageFont.load_default()

        stitle = truncate(title)
        draw.text((565, 180), stitle[0], (255, 255, 255), font=tfont)
        draw.text((565, 230), stitle[1], (255, 255, 255), font=tfont)
        draw.text((565, 320), f"{channel} | {views[:23]}", (255, 255, 255), font=arial)

        # Progress bar + animation effect (subtle)
        draw.line([(565, 385), (1130, 385)], fill="white", width=8, joint="curve")
        progress_end = random.randint(600, 999)
        draw.line([(565, 385), (progress_end, 385)], fill=rand_color, width=8, joint="curve")
        draw.ellipse([(progress_end, 375), (progress_end+21, 395)], outline=rand_color, fill=rand_color, width=15)
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

        # Optional: create subtle glow animation (2 frames)
        frame1 = background.copy()
        frame2 = ImageEnhance.Brightness(background).enhance(1.2)
        tpath = f"cache/{videoid}.gif"
        frame1.save(tpath, save_all=True, append_images=[frame2], duration=500, loop=0)
        return tpath

    except Exception:
        traceback.print_exc()
        return None
