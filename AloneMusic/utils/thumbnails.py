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
EMOJI_ICON = "🎵"

os.makedirs(CACHE_DIR, exist_ok=True)

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))

def truncate(text, limit=30):
    words = text.split(" ")
    text1, text2 = "", ""
    for i in words:
        if len(text1)+len(i) < limit: text1 += " " + i
        elif len(text2)+len(i) < limit: text2 += " " + i
    return [text1.strip(), text2.strip()]

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
            youtube = Image.open(f"{CACHE_DIR}/thumb{videoid}.png").convert("RGBA")
        except Exception:
            youtube = Image.open(DEFAULT_IMAGE).convert("RGBA")

        # Base background
        image1 = changeImageSize(1280, 720, youtube)
        background_base = image1.filter(ImageFilter.GaussianBlur(20))
        background_base = ImageEnhance.Brightness(background_base).enhance(0.6)

        # Crop logo multiple angles
        Xc, Yc = youtube.width / 2, youtube.height / 2
        logos = []
        for i in range(10):
            angle = random.randint(-25, 25)
            x1, y1 = Xc - 150, Yc - 150
            x2, y2 = Xc + 150, Yc + 150
            logo = youtube.crop((x1, y1, x2, y2))
            logo.thumbnail((150,150))
            logo = logo.rotate(angle, expand=True)
            rand_color = tuple(random.randint(50,200) for _ in range(3))
            logo = ImageOps.expand(logo, border=10, fill=rand_color)
            logos.append(logo)

        def draw_text(draw_obj, stitle, channel, views, frame_num):
            try:
                font1 = ImageFont.truetype(f"{ASSETS_DIR}/font2.ttf", 40)
                font2 = ImageFont.truetype(f"{ASSETS_DIR}/font3.ttf", 55)
            except:
                font1 = font2 = ImageFont.load_default()

            # Gradient multi-color text
            for idx, line in enumerate(stitle):
                color = tuple(random.randint(200,255) for _ in range(3))
                draw_obj.text((565, 180 + idx*60), line, fill=color, font=font2, stroke_width=2, stroke_fill=(0,0,0))
            
            draw_obj.text((565, 320), f"{channel} | {views[:23]}", (255,255,255), font=font1)
            emoji_x = 565 + (frame_num*25 % 300)
            draw_obj.text((emoji_x, 500), EMOJI_ICON, (255,255,255), font=font1)

        # Create animated frames
        frames = []
        stitle = truncate(title)
        for fnum in range(6):
            bg = background_base.copy()
            draw = ImageDraw.Draw(bg)
            # Paste logos at different positions & angles
            for i, logo in enumerate(logos):
                x = 100 + (i%5)*220 + random.randint(-15,15)
                y = 450 + (i//5)*180 + random.randint(-10,10)
                shadow = Image.new("RGBA", logo.size, (0,0,0,100))
                bg.paste(shadow, (x+5,y+5), shadow)
                bg.paste(logo, (x,y), logo)
            factor = 0.9 + (fnum%2)*0.15
            bg = ImageEnhance.Brightness(bg).enhance(factor)
            draw_text(draw, stitle, channel, views, fnum)
            frames.append(bg)

        # Optional icons overlay
        try:
            icons = Image.open(f"{ASSETS_DIR}/icons.png").resize((580,62))
            for frame in frames:
                frame.paste(icons, (565,450), icons if icons.mode=="RGBA" else None)
        except:
            pass

        # Cleanup temp
        try:
            os.remove(f"{CACHE_DIR}/thumb{videoid}.png")
        except:
            pass

        # Save animated GIF
        tpath = f"{CACHE_DIR}/{videoid}.gif"
        frames[0].save(tpath, save_all=True, append_images=frames[1:], duration=200, loop=0)
        return tpath

    except Exception:
        traceback.print_exc()
        return None
