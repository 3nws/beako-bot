import requests

from bs4 import BeautifulSoup

from commands.db.classes.Scrape_Series import Scrape_Series


class Re_zero(Scrape_Series):

    def __init__(self, url):
        self.url = url

    def scrape(self):
        try:
            # web scraping for re zero
            try:
                page = requests.get(self.url, timeout=5)
            except requests.Timeout:
                print("WitchCultTranslation down!")
                return

            soup = BeautifulSoup(page.content, 'html.parser')
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
