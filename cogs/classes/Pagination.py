import discord

from discord import ui
from discord.ext import menus
from typing import Union, Any

class Source(menus.ListPageSource):
    async def format_page(self, menu, entries):
        return f"This is number {entries}."

class MangaReader(ui.View, menus.MenuPages):
    def __init__(self, source: Source):
        super().__init__(timeout=60)
        self._source: Source = source
        self.current_page: int = 0
        self.i: Union[discord.Interaction, None] = None
        self.msg: Union[discord.Message, None] = None
        self.embed: Union[discord.Embed, None] = None
        self.text: Union[str, None] = None
        self.group: Union[str, None] = None

    async def start(self, *, interaction: discord.Interaction, channel: discord.TextChannel, text: str, embed: discord.Embed, group: str):
        await self._source._prepare_once()
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        kwargs['content'] = text
        kwargs['embed'] = embed
        self.msg = await channel.send(**kwargs)
        self.embed = embed
        self.text = text
        self.group = group
        self.i = interaction

    async def _get_kwargs_from_page(self, page: str):
        value = {}
        if 'view' not in value:
            value['view'] = self
        return value

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        btn_usr: discord.User = interaction.user
        i_usr: discord.User = self.i.user
        return True if self.i is None else btn_usr == i_usr

    async def on_timeout(self):
        self.stop()
        await self.msg.edit(content=self.text, embed=self.embed, view=self.disabled())
        await self.msg.reply("This view just timed out, I suppose! You need to interact with it to keep it up, in fact!")

    async def turn_page(self, page_num: int):
        page: Union[Any, List[Any]] = await self._source.get_page(page_num)
        self.current_page = page_num
        kwargs = await self._get_kwargs_from_page(page)
        kwargs['content'] = self.text
        self.embed.set_image(url=page)
        self.embed.set_footer(text=(f"Page {page_num+1}/{self._source._max_pages}. Translated by " + self.group))
        kwargs['embed'] = self.embed
        await self.msg.edit(**kwargs)

    def disabled(self):
        for btn in self._children:
            btn.disabled = True
        return self

    @ui.button(emoji='<:before_fast_check:754948796139569224>', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]):
        await interaction.response.defer()
        await self.turn_page(0)

    @ui.button(emoji='<:before_check:754948796487565332>', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]):
        await interaction.response.defer()
        await self.turn_page(self.current_page - 1)

    @ui.button(emoji='<:stop_check:754948796365930517>', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]):
        self.stop()
        await interaction.response.defer()
        await self.msg.edit(content=self.text, embed=self.embed, view=self.disabled())

    @ui.button(emoji='<:next_check:754948796361736213>', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]):
        await interaction.response.defer()
        await self.turn_page(self.current_page + 1)

    @ui.button(emoji='<:next_fast_check:754948796391227442>', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]):
        await interaction.response.defer()
        await self.turn_page(self._source.get_max_pages() - 1)

