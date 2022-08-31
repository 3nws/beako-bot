import discord
import json

from typing import Optional, Any, List, Dict
from aiohttp import ClientSession

from Bot import Bot


class Chapter:

    __slots__ = (
        "id",
        "title",
        "num",
        "lang",
        "pages",
        "link",
        "images",
        "scanlation",
    )

    def __init__(
        self,
        id: str,
        title: str,
        num: str,
        lang: str,
        pages: str,
        link: str,
        images: List[str],
        scanlation: str,
    ):
        self.id = id
        self.title = title
        self.num = num
        self.lang = lang
        self.pages = pages
        self.link = link
        self.images = images
        self.scanlation = scanlation

    def get_title(self):
        title = self.title if self.title is not None else self.id
        is_title = title != self.id
        return [title, is_title]

    def get_link(self):
        return self.link


class MangaDex:
    def __init__(self, bot: Bot):
        self.base_manga_url = "https://api.mangadex.org/manga/"
        self.base_chapter_url = "https://api.mangadex.org/chapter"
        self.base_read_url = "https://mangadex.org/chapter/"
        self.base_manga_info_url = "https://mangadex.org/manga/"
        self.cover_url = "https://uploads.mangadex.org/covers/"
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        self.scanlation_base_url = "https://api.mangadex.org/group/"
        self.bot = bot

    async def search(self, query: str, limit: str) -> Optional[List[Any]]:
        url = (
            self.base_manga_url
            + f"?limit={limit}&title={query}&availableTranslatedLanguage%5B%5D=en&order%5Btitle%5D=asc"
        )

        session: ClientSession = self.bot.session
        async with session.get(url) as res:
            if res.status == 200:
                resp = await res.read()
                r = json.loads(resp)
            else:
                print("Something went wrong with the MangaDex request!")
                return
        r = r["data"]
        embed = discord.Embed(
            title=f"Pick one of the results for '{query}', I suppose!",
            color=discord.Colour.random(),
        )

        titles: List[str] = []
        manga_ids: List[str] = []
        for i, rs in enumerate(r):
            manga_ids.append(rs["id"])
            info = rs["attributes"]
            title = (info["title"])["en"]
            titles.append(title)
            title += f" {self.emojis[i]}"
            link = self.base_manga_info_url + rs["id"]
            desc = f"on [MangaDex]({link})\n"
            if info["description"]:
                desc += (info["description"])["en"]
            embed.add_field(name=title, value=desc[:300] + "...", inline=False)

        return [self.emojis, embed, titles, manga_ids]

    def get_following(self, channel_id: str):
        pass

    async def get_manga_title(self, id: str) -> Optional[str]:
        url: str = self.base_manga_url + id
        session: ClientSession = self.bot.session
        async with session.get(url) as res:
            if res.status == 200:
                resp = await res.read()
                r = json.loads(resp)
            else:
                print("Something went wrong with the MangaDex request!")
                return
        r = r["data"]
        return r["attributes"]["title"]["en"]

    async def get_scanlation_group(self, id: str) -> Optional[Dict[str, str]]:
        url: str = self.scanlation_base_url + id
        session: ClientSession = self.bot.session
        async with session.get(url) as res:
            if res.status == 200:
                resp = await res.read()
                r = json.loads(resp)
                return r
            else:
                print("Something went wrong with the MangaDex request!")
                return

    async def get_latest(self, id: str) -> Optional[Chapter]:
        url: str = (
            self.base_chapter_url
            + "?limit=5&manga="
            + id
            + "&translatedLanguage%5B%5D=en&order%5Bvolume%5D=desc&order%5Bchapter%5D=desc&excludedGroups%5B%5D=4f1de6a2-f0c5-4ac5-bce5-02c7dbb67deb"
        )
        session: ClientSession = self.bot.session
        async with session.get(url) as res:
            if res.status == 200:
                resp = await res.read()
                r = json.loads(resp)
            else:
                print("Something went wrong with the MangaDex request!")
                return
        data = r["data"]
        if len(data) == 0:
            url = (
                self.base_chapter_url
                + "?limit=5&manga="
                + id
                + "&translatedLanguage%5B%5D=en&order%5Bvolume%5D=desc&order%5Bchapter%5D=desc"
            )
            session = self.bot.session
            async with session.get(url) as res:
                if res.status == 200:
                    resp = await res.read()
                    r = json.loads(resp)
                else:
                    print("Something went wrong with the MangaDex request!")
                    return
        data = r["data"]
        scanlation_id = data[0]["relationships"][0]["id"]
        attrs = data[0]["attributes"]
        chapter_id = data[0]["id"]
        chapter_title = attrs["title"]
        chapter_num = attrs["chapter"]
        translated_lang = attrs["translatedLanguage"]
        num_of_pages = attrs["pages"]
        chapter_link = self.base_read_url + data[0]["id"] + "/1"

        url = f"https://api.mangadex.org/at-home/server/{chapter_id}"
        image_urls: List[str] = []
        session: ClientSession = self.bot.session
        async with session.get(url) as res:
            if res.status == 200:
                resp = await res.read()
                image_server_url = json.loads(resp)
                chapter_hash = image_server_url["chapter"]["hash"]
                chapter_data = image_server_url["chapter"]["data"]
                image_server_url = image_server_url["baseUrl"].replace("\\", "")
                image_server_url = f"{image_server_url}/data"
                for filename in chapter_data:
                    image_urls.append(f"{image_server_url}/{chapter_hash}/{filename}")

        chapter = Chapter(
            chapter_id,
            chapter_title,
            chapter_num,
            translated_lang,
            num_of_pages,
            chapter_link,
            image_urls,
            scanlation_id,
        )

        return chapter

    async def get_info(self, query: str) -> Optional[discord.Embed]:
        if query:
            url = (
                self.base_manga_url
                + f"?limit=1&title={query}&availableTranslatedLanguage%5B%5D=en"
            )
            session: ClientSession = self.bot.session
            async with session.get(url) as res:
                if res.status == 200:
                    resp = await res.read()
                    r = json.loads(resp)
                else:
                    print("Something went wrong with the MangaDex request!")
                    return None
            r = r["data"]
            if r == []:
                return None
            rs = r[0]
            manga_id = rs["id"]
            manga_info_url = (
                self.base_manga_url
                + manga_id
                + "?includes%5B%5D=cover_art&includes%5B%5D=author&includes%5B%5D=artist"
            )
            session = self.bot.session
            async with session.get(manga_info_url) as res:
                if res.status == 200:
                    resp = await res.read()
                    r = json.loads(resp)
                else:
                    print("MangaReader down!")
                    return
            rs = r["data"]
            info = rs["attributes"]
            title = (info["title"])["en"]
            link = self.base_manga_info_url + rs["id"]
            desc = f"on [MangaDex]({link})\n"
            if info["description"]:
                desc += (info["description"])["en"]
            rels = rs["relationships"]
            cover_filename = None
            for rel in rels:
                if rel["type"] == "cover_art":
                    cover_filename = rel["attributes"]["fileName"]
            cover_url = self.cover_url + manga_id + "/" + cover_filename
            embed = discord.Embed(
                title=f"{title}",
                color=discord.Colour.random(),
                description=desc,
            )
            embed.set_image(url=cover_url)
            return embed
        else:
            return discord.Embed(
                title="What info do you want, in fact! Tell me a manga, I suppose!",
                color=discord.Colour.random(),
            )
