import requests

class MangaDex:
    
    def __init__(self):
        self.base_manga_url = 'https://api.mangadex.org/manga/'
        self.base_chapter_url = 'https://api.mangadex.org/chapter/'
        self.base_read_url = 'https://mangadex.org/chapter/'
        
    def get_latest(self, id):
        s = requests.session()
        r = s.get(self.base_manga_url+id+'/aggregate')
        r = r.json()
        chp_count = ((r['volumes'])['none'])['count']
        chapters = ((r['volumes'])['none'])['chapters']
        last_chp = chapters[str(chp_count-1)]
        last_chp_id = last_chp['id']
        r = s.get(self.base_chapter_url+last_chp_id)
        r = r.json()
        chapter_title = ((r['data'])['attributes'])['title']
        chapter_num = ((r['data'])['attributes'])['chapter']
        translated_lang = ((r['data'])['attributes'])['translatedLanguage']
        num_of_pages = ((r['data'])['attributes'])['pages']
        chapter_link = self.base_read_url+last_chp_id+'/1'
        if chapter_title==None:
            # add only the chapter num to the embed
            # else add title with chapter num
            pass
        
        
        
        
        
