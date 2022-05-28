import aiohttp
import html5lib

from bs4 import BeautifulSoup

from commands.db.classes.Scrape_Series import Scrape_Series


class Guya_moe(Scrape_Series):
    def __init__(self, url, bot):
        self.url = url
        self.bot = bot

    async def scrape(self):
        try:
            # web scraping for guya.moe
            session = self.bot.session
            async with session.get(self.url) as r:
                if r.status == 200:
                    page = await r.read()
                else:
                    print("Guya.moe down!")
                    return

            soup = BeautifulSoup(page.decode('utf-8'), "html5lib")

            most_recent_chapter = soup.find_all("td", "chapter-title")[0]

            chapter_link = most_recent_chapter.find("a")

            if "href" in chapter_link.attrs:
                chapter_anchor = "https://guya.moe"
                chapter_anchor += chapter_link.get("href")

            most_recent_chapter_title = chapter_link.text

            most_recent_chapter_array = most_recent_chapter_title.split()

            most_recent_chapter_str = ""

            # start from 2 to work around the spoiler-free titles
            for i in range(2, len(most_recent_chapter_array)):
                most_recent_chapter_str += most_recent_chapter_array[i] + " "

            most_recent_chapter_str = most_recent_chapter_str.strip()

            return [most_recent_chapter_str, chapter_anchor]
        except Exception as e:
            print(e)

    async def latest_chapter(self):
        try:
            scrape_results = await self.scrape()
            title = scrape_results[0]
            anchor = scrape_results[1]
            return f"'{title}' has been translated.\n{anchor}, I suppose!"
        except Exception as e:
            print(e)
