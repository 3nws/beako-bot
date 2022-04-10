import requests
import discord

class MangaDex:
    
    def __init__(self):
        self.base_manga_url = 'https://api.mangadex.org/manga/'
        self.base_chapter_url = 'https://api.mangadex.org/chapter'
        self.base_read_url = 'https://mangadex.org/chapter/'
        self.base_manga_info_url = 'https://mangadex.org/manga/'
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        
    def search(self, query, limit):
        url = self.base_manga_url + \
            f'?limit={limit}&title={query}&availableTranslatedLanguage%5B%5D=en'
        
        s = requests.session()
        r = s.get(url)
        r = (r.json())['data']
        embed = discord.Embed(
            title = f"Pick one of the results for '{query}', I suppose!",
            color = discord.Colour.random(),
        )
        
        titles = []
        manga_ids = []
        for i, rs in enumerate(r):
            manga_ids.append(rs['id'])
            info = rs['attributes']
            title = (info['title'])['en']
            titles.append(title)
            title += f' {self.emojis[i]}'
            link = self.base_manga_info_url+rs['id']
            desc = f"on [MangaDex]({link})\n"
            if info['description']:
                desc += (info['description'])['en']
            embed.add_field(name=title, value=desc[:300]+'...', inline=False)
        
        
        return [self.emojis, embed, titles, manga_ids]
       
    def get_id(self, title):
        manga_id = self.search(title, 1)[-1][0]
        return manga_id
     
    def get_latest(self, id):
        s = requests.session()
        url = self.base_chapter_url+'?limit=5&manga='+id + \
            '&translatedLanguage%5B%5D=en&order%5Bvolume%5D=desc&order%5Bchapter%5D=desc'
        r = s.get(url)
        r = r.json()
        data = r['data']
        attrs = data[0]['attributes']
        chapter_title = attrs['title']
        chapter_num = attrs['chapter']
        translated_lang = attrs['translatedLanguage']
        num_of_pages = attrs['pages']
        chapter_link = self.base_read_url+data[0]['id']+'/1'
        return chapter_title
        if chapter_title==None:
            # add only the chapter num to the embed
            # else add title with chapter num
            pass
        
        
        
        
        
