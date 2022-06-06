import html5lib      # type: ignore

from bs4 import BeautifulSoup
from typing import Tuple, Union, Any, Optional
from aiohttp import ClientSession

from Bot import Bot
from commands.db.classes.Scrape_Series import Scrape_Series


class Grand_Blue(Scrape_Series):

    __slots__ = (
        "url",
        "bot"
    )
    

    def __init__(self, url: str, bot: Bot):
        self.url = url
        self.bot = bot

    async def scrape(self) -> Union[Tuple[str, str], Any]:
        try:
            # web scraping for grand-blue mangareader
            session: ClientSession = self.bot.session  
            async with session.get(self.url) as r:
                if r.status == 200:
                    page = await r.read()
                else:
                    print("MangaReader down!")
                    return

            soup = BeautifulSoup(page.decode('utf-8'), "html5lib")

            most_recent_chapter = soup.find_all(
                "li", "item reading-item chapter-item")[0]

            chapter_link = most_recent_chapter.find("a")
            chapter_anchor = ""
            if "href" in chapter_link.attrs:
                chapter_anchor = "https://mangareader.to"
                chapter_anchor += chapter_link.get("href")

            most_recent_chapter_title = chapter_link.get('title')

            return [most_recent_chapter_title, chapter_anchor]

        except Exception as e:
            print(e)

    async def latest_chapter(self) -> Optional[str]:
        try:
            scrape_results = await self.scrape()
            title = scrape_results[0]
            anchor = scrape_results[1]
            return f"'{title}' has been translated.\n{anchor}, I suppose!"
        except Exception as e:
            print(e)
