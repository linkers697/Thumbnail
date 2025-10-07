import os
import re
import random
import aiohttp
import aiofiles
import traceback
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch

DEFAULT_IMAGE = "AloneMusic/assets/default.png"
CACHE_DIR = "cache"
ASSETS_DIR = "AloneMusic/assets"
EMOJI_ICON = "🎵"  # Emoji for moving effect

os.makedirs(CACHE_DIR, exist_ok=True)

def changeImageSize(maxWidth, maxHeight, image):
    try:
        widthRatio = maxWidth / image.size[0]
        heightRatio = maxHeight / image.size[1]
        newWidth = int(widthRatio * image.size[0])
        newHeight = int(heightRatio * image.size[1])
        return image.resize((newWidth, newHeight))
    except Exception:
        return image

def truncate(text, limit=30):
    try:
        words = text.split(" ")
        text1, text2 = "", ""
        for i in words:
            if len(text1) + len(i) < limit:
                text1 += " " + i
            elif len(text2) + len(i) < limit:
                text2 += " " + i
        return [text1.strip(), text2.strip()]
    except Exception:
        return ["Title", ""]

async def get_thumb(videoid: str):
    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        result_data = await results.next()
        result = result_data.get("result", [{}])[0]

        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
        thumbnail_url = result.get("thumbnails", [{"url": DEFAULT_IMAGE}])[0].get("url", DEFAULT_IMAGE).split("?")[0]

        # Fetch thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"{CACHE_DIR}/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())

        # Open safely
        try:
            youtube = Image.open(f"{CACHE_DIR}/thumb{videoid}.png")
        except Exception:
            youtube = Image.open(DEFAULT_IMAGE)

        # Base background
        image1 = changeImageSize(1280, 720, youtube)
        background_base = image1.convert("RGBA").filter(ImageFilter.GaussianBlur(20))
        background_base = ImageEnhance.Brightness(background_base).enhance(0.6)

        # Crop logo
        Xc, Yc = youtube.width / 2, youtube.height / 2
        x1, y1 = Xc - 250, Yc - 250
        x2, y2 = Xc + 250, Yc + 250
        rand_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((370, 370), Image.ANTIALIAS)
        logo = ImageOps.expand(logo, border=17, fill=rand_color)

        # Draw function
        def draw_text(draw_obj, stitle, channel, views, frame_num):
            try:
                arial = ImageFont.truetype(f"{ASSETS_DIR}/font2.ttf", 30)
                tfont = ImageFont.truetype(f"{ASSETS_DIR}/font3.ttf", 45)
            except Exception:
                arial = tfont = ImageFont.load_default()
            draw_obj.text((565, 180), stitle[0], (255, 255, 255), font=tfont)
            draw_obj.text((565, 230), stitle[1], (255, 255, 255), font=tfont)
            draw_obj.text((565, 320), f"{channel} | {views[:23]}", (255, 255, 255), font=arial)
            emoji_x = 565 + (frame_num * 20 % 200)
            draw_obj.text((emoji_x, 500), EMOJI_ICON, (255, 255, 255), font=arial)

        # Create frames for animation
        frames = []
        stitle = truncate(title)
        for fnum in range(6):
            bg = background_base.copy()
            bg.paste(logo, (100, 150), logo if logo.mode=="RGBA" else None)
            draw = ImageDraw.Draw(bg)
            factor = 0.9 + (fnum % 2) * 0.2
            bg = ImageEnhance.Brightness(bg).enhance(factor)
            draw_text(draw, stitle, channel, views, fnum)
            frames.append(bg)

        # Overlay icons if available
        try:
            icons = Image.open(f"{ASSETS_DIR}/icons.png").resize((580,62))
            for frame in frames:
                frame.paste(icons, (565,450), icons if icons.mode=="RGBA" else None)
        except Exception:
            pass

        # Cleanup temp
        try:
            os.remove(f"{CACHE_DIR}/thumb{videoid}.png")
        except Exception:
            pass

        # Save GIF
        tpath = f"{CACHE_DIR}/{videoid}.gif"
        frames[0].save(tpath, save_all=True, append_images=frames[1:], duration=200, loop=0)
        return tpath

    except Exception:
        traceback.print_exc()
        return None
