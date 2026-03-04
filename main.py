import os
import asyncio
from telethon import TelegramClient, events
from playwright.async_api import async_playwright

# 1. ሚስጢር ቁልፎችን ከ GitHub Secrets መውሰድ
API_ID = int(os.environ.get('TG_API_ID', 0))
API_HASH = os.environ.get('TG_API_HASH', '')
WEB_USER = os.environ.get('WEB_USER', '')
WEB_PASS = os.environ.get('WEB_PASS', '')

# የቴሌግራም ክሊየንት ማዘጋጀት
client = TelegramClient('session', API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    # በቴሌግራም ላይ ምስል ያለበት አዲስ መልዕክት ሲመጣ
    if event.photo:
        print("አዲስ ማስታወቂያ ተገኝቷል፣ ወደ zv.free.nf እየጫንኩ ነው...")
        
        # ምስሉን ለጊዜው ማውረድ
        path = await event.download_media()
        # የጽሁፉን የመጀመሪያ መስመር ለርዕስ መጠቀም
        full_text = event.raw_text or "No Description"
        product_name = full_text.split('\n')[0][:30] # የመጀመሪያዋን መስመር ለስም መውሰድ

        async with async_playwright() as p:
            # ብሮውዘሩን መክፈት
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 2. ሎግ-ኢን ማድረግ
                await page.goto("https://zv.free.nf/login.php") # እዚህ ጋር ትክክለኛውን የሎግ-ኢን ገጽ ያረጋግጡ
                await page.fill('input[name="username"]', WEB_USER)
                await page.fill('input[name="password"]', WEB_PASS)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state("networkidle")

                # 3. ወደ አፕሎድ ፎርሙ መሄድ
                await page.goto("https://zv.free.nf/add_product.php") # ምስሉ ላይ ያየነው ገጽ
                
                # ፎርሙን መሙላት
                await page.set_input_files('input[type="file"]', path)
                await page.fill('input[placeholder*="Product Name"]', product_name)
                await page.fill('input[placeholder*="Price"]', "Contact Seller")
                await page.fill('input[placeholder*="Detail 1"]', full_text)
                
                # 4. Upload ቁልፍን መጫን
                await page.click('button:has-text("Upload")')
                await page.wait_for_timeout(3000) # ለ3 ሰከንድ መጠበቅ
                
                print(f"በተሳካ ሁኔታ ተጭኗል: {product_name}")
            
            except Exception as e:
                print(f"ስህተት ተከስቷል: {e}")
            
            finally:
                await browser.close()
                if os.path.exists(path):
                    os.remove(path) # የወረደውን ምስል ማጥፋት

# ቦቱን ማስጀመር
print("ሰራተኛው (Bot) ስራ ጀምሯል... ቴሌግራምን እየጠበቀ ነው")
client.start()
client.run_until_disconnected()
