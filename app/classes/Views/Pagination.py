import discord

from discord import ui
from discord.ext import menus
from typing import Union, Any, Optional, List
from typing_extensions import Self

Channel = Union[
    discord.abc.GuildChannel,
    discord.Thread,
    discord.abc.PrivateChannel,
    discord.PartialMessageable,
    None,
]


class Source(menus.ListPageSource):
    async def format_page(self, menu, entries):  # type: ignore
        return f"This is number {entries}."


class MangaReader(ui.View, menus.MenuPages):
    __slots__ = (
        "_source",
        "current_page",
        "i",
        "msg",
        "embed",
        "text",
        "group",
    )

    def __init__(self, source: Source):
        super().__init__(timeout=None)
        self._source: Source = source
        self.current_page: int = 0
        self.i: Optional[discord.Interaction]
        self.msg: Optional[discord.Message]
        self.embed: Optional[discord.Embed]
        self.text: Optional[str]
        self.group: Optional[str]

    async def start(  # type: ignore
        self,
        *,
        interaction: Optional[discord.Interaction],
        channel: Channel,
        text: str,
        embed: discord.Embed,
        group: Optional[str],
        is_task: bool = False,
    ):
        await self._source._prepare_once()  # type: ignore
        page = await self._source.get_page(0)  # type: ignore
        kwargs = await self._get_kwargs_from_page(page)  # type: ignore
        kwargs["content"] = text
        kwargs["embed"] = embed
        self.msg = await channel.send(**kwargs)  # type: ignore
        self.embed = embed
        self.text = text
        self.group = group
        self.i = interaction
        self.is_task = is_task

    async def _get_kwargs_from_page(self, page: str):  # type: ignore
        value = {}
        if "view" not in value:
            value["view"] = self
        return value  # type: ignore

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        await interaction.response.defer()
        if self.is_task:
            return True
        btn_usr: Union[discord.Member, discord.User] = interaction.user
        i_usr: Union[discord.Member, discord.User] = self.i.user
        cond: bool = True if self.i is None else btn_usr == i_usr
        if not cond:
            await interaction.followup.send(
                "That's not your view, in fact!", ephemeral=True
            )
        return cond

    async def on_timeout(self):
        self.stop()
        await self.msg.edit(content=self.text, embed=self.embed, view=self.disabled())
        # await self.msg.reply(
        #     "This view just timed out, I suppose! You need to interact with it to keep it up, in fact!"
        # )

    async def turn_page(self, page_num: int):
        page: Union[Any, List[Any]] = await self._source.get_page(page_num)  # type: ignore
        self.current_page = page_num
        kwargs = await self._get_kwargs_from_page(page)  # type: ignore
        kwargs["content"] = self.text
        self.embed.set_image(url=page)
        group = self.group or "Unknown"
        self.embed.set_footer(
            text=(
                f"Page {page_num+1}/{self._source._max_pages}. Translated by "  # type: ignore
                + group
            )
        )
        kwargs["embed"] = self.embed
        await self.msg.edit(**kwargs)

    def disabled(self):
        for btn in self.children:
            btn.disabled = True  # type: ignore
        return self

    @ui.button(
        emoji="⏮️",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:first",
    )
    async def first_page(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.turn_page(0)

    @ui.button(
        emoji="⏪",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:previous",
    )
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.turn_page(self.current_page - 1)

    @ui.button(
        emoji="⏹️",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:stop",
    )
    async def stop_page(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        self.stop()
        await self.msg.edit(content=self.text, embed=self.embed, view=self.disabled())

    @ui.button(
        emoji="⏩",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:next",
    )
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.turn_page(self.current_page + 1)

    @ui.button(
        emoji="⏭️",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:last",
    )
    async def last_page(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.turn_page(self._source.get_max_pages() - 1)
