import requests
import discord

class MangaDex:
    
    def __init__(self):
        self.base_manga_url = 'https://api.mangadex.org/manga/'
        self.base_chapter_url = 'https://api.mangadex.org/chapter/'
        self.base_read_url = 'https://mangadex.org/chapter/'
        self.base_manga_info_url = 'https://mangadex.org/manga/'
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        
    def search(self, query):
        url = self.base_manga_url+f'?limit=5&title={query}&includedTagsMode=AND&excludedTagsMode=OR&availableTranslatedLanguage%5B%5D=en&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5BlatestUploadedChapter%5D=desc'

        s = requests.session()
        r = s.get(url)
        r = (r.json())['data']
        embed = discord.Embed(
            title = f"Pick one of the results for {query}, I suppose!",
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
            desc += (info['description'])['en']
            embed.add_field(name=title, value=desc[:500]+'...', inline=False)
        
        
        return [self.emojis, embed, titles, manga_ids]
        
    def get_latest(self, id):
        s = requests.session()
        url = self.base_manga_url+id+'/aggregate'
        r = s.get(url)
        r = r.json()
        chp_count = ((r['volumes'])['none'])['count']
        chapters = ((r['volumes'])['none'])['chapters']
        last_chp = chapters[str(chp_count-1)]
        last_chp_id = last_chp['id']
        url = self.base_chapter_url+last_chp_id
        r = s.get(url)
        r = r.json()
        chapter_title = ((r['data'])['attributes'])['title']
        chapter_num = ((r['data'])['attributes'])['chapter']
        translated_lang = ((r['data'])['attributes'])['translatedLanguage']
        num_of_pages = ((r['data'])['attributes'])['pages']
        chapter_link = self.base_read_url+last_chp_id+'/1'
        return chapter_title
        if chapter_title==None:
            # add only the chapter num to the embed
            # else add title with chapter num
            pass
        
        
        
        
        
