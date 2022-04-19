import aiohttp
import html5lib

from bs4 import BeautifulSoup

from commands.db.classes.Scrape_Series import Scrape_Series


class Re_zero(Scrape_Series):

    def __init__(self, url):
        self.url = url

    async def scrape(self):
        try:
            # web scraping for re zero
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as r:
                    if r.status == 200:
                        page = await r.read()
                    else:
                        print("WitchCultTranslation down!")
                        return

            soup = BeautifulSoup(page.decode('utf-8'), "html5lib")
            
            most_recent_post = soup.find_all('h3', 'rpwe-title')[0]

            post_link = most_recent_post.find('a')

            most_recent_post = most_recent_post.text
            most_recent_post_array = most_recent_post.split()

            most_recent_post_str = ""

            for i in range(0, 4):
                most_recent_post_str += most_recent_post_array[i] + " "

            most_recent_post_str = most_recent_post_str.strip()

            if 'href' in post_link.attrs:
                chapter_link = post_link.get('href')

            return [most_recent_post_str, chapter_link]
        except Exception as e:
            print(e)

    def latest_chapter(self):
        try:
            scrape_results = self.scrape()
            title = scrape_results[0]
            anchor = scrape_results[1]
            return f"'{title}' has been translated.\n{anchor}, I suppose!"
        except Exception as e:
            print(e)
