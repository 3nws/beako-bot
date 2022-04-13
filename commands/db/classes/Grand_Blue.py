import requests

from bs4 import BeautifulSoup

from commands.db.classes.Scrape_Series import Scrape_Series


class Grand_Blue(Scrape_Series):
    def __init__(self, url):
        self.url = url

    def scrape(self):
        try:
            # web scraping for grand-blue mangareader
            try:
                page = requests.get(self.url, timeout=5)
            except requests.Timeout:
                print("mangareader down!")
                return

            soup = BeautifulSoup(page.content, "html.parser")

            most_recent_chapter = soup.find_all("li", "item reading-item chapter-item")[
                0
            ]

            chapter_link = most_recent_chapter.find("a")

            if "href" in chapter_link.attrs:
                chapter_anchor = "https://mangareader.to"
                chapter_anchor += chapter_link.get("href")

            most_recent_chapter_title = chapter_link.get("title")

            return [most_recent_chapter_title, chapter_anchor]

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
