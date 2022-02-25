import requests

from bs4 import BeautifulSoup
from time import sleep

from commands.db.classes.Scrape_Series import Scrape_Series

class Guya_moe(Scrape_Series):
    
    def __init__(self, url):
      self.url = url
    
    def scrape(self):
      try:
        # web scraping for guya.moe
        is_guya_down = False
        try:
          page = requests.get(self.url, timeout=5)
        except requests.Timeout:
          print("Guya.moe down!")
          is_guya_down = True
          sleep(1)
          return
        
        soup = BeautifulSoup(page.content, 'html.parser')
    
        most_recent_chapter = soup.find_all('td', 'chapter-title')[0]
    
        chapter_link = most_recent_chapter.find('a')

        if 'href' in chapter_link.attrs:
          chapter_anchor = 'https://guya.moe'
          chapter_anchor += chapter_link.get('href')

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
        
        
    def latest_chapter(self):
      try:
        # web scraping for guya.moe
        is_guya_down = False
        try:
          page = requests.get(self.url, timeout=5)
        except requests.Timeout:
          print("Guya.moe down!")
          is_guya_down = True
          return
        
        soup = BeautifulSoup(page.content, 'html.parser')

        most_recent_chapter = soup.find_all('td', 'chapter-title')[0]

        chapter_link = most_recent_chapter.find('a')

        if 'href' in chapter_link.attrs:
          anchor = 'https://guya.moe'
          anchor += chapter_link.get('href')

        most_recent_chapter_title = chapter_link.text

        most_recent_chapter_array = most_recent_chapter_title.split()

        title = ""

        # start from 2 to work around the spoiler-free titles
        for i in range(2, len(most_recent_chapter_array)):
          title += most_recent_chapter_array[i] + " "

        title = title.strip()

        return f'Chapter {title} has been translated.\n{anchor}, I suppose!'
      except Exception as e:
        print(e)