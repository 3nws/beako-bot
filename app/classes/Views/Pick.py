import discord
import json

from discord import ui
from typing import Tuple, Dict, Optional, List
from typing_extensions import Self

from classes.MangaDex import MangaDex, Chapter
from Bot import Bot


class PickView(ui.View):
    __slots__ = (
        "i",
        "mangas",
        "bot",
        "md",
        "info",
        "num_of_results",
        "embed",
        "ignore_individual",
    )

    def __init__(
        self,
        i: discord.Interaction,
        info: Tuple[List[str], List[str]],
        bot: Bot,
        embed: discord.Embed,
        *,
        ignore_individual: Optional[bool] = False,
    ):
        super().__init__(timeout=None)
        self.i = i
        self.mangas: Dict[str, str] = {}
        self.bot = bot
        self.db = self.bot.db
        self.md: MangaDex = MangaDex(self.bot)
        self.info = info
        self.num_of_results: int = len(self.info[0])
        self.embed = embed
        self.ignore_individual = ignore_individual
        if self.num_of_results != len(self.children):
            if self.i.command.name == "add":
                start = len(self.children) - 2
            else:
                start = len(self.children) - 1
            for j in range(start, self.num_of_results - 1, -1):
                self.remove_item(self.children[j])

    def disabled(self):
        for btn in self.children:
            btn.disabled = True  # type: ignore
        return self

    async def on_timeout(self):
        self.stop()
        await self.i.edit_original_response(embed=self.embed, view=self.disabled())
        msg = await self.i.original_response()
        # await msg.reply(
        #     "This view just timed out, I suppose! You need to interact with it to keep it up, in fact!"
        # )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        await interaction.response.defer()
        cond: bool = interaction.user == self.i.user
        if not cond:
            await interaction.followup.send(
                "That's not your view, in fact!", ephemeral=True
            )
        return cond

    async def find_one(self):
        query = "SELECT * FROM mangadex WHERE channel_id = $1 AND guild_id = $2"
        channel_exist = (
            len(await self.bot.db.fetch(query, self.i.channel_id, self.i.guild.id)) != 0
        )
        if not channel_exist:
            connection = await self.db.acquire()
            async with connection.transaction():
                query = "INSERT INTO mangadex (guild_id, channel_id, mangas, ignore_no_group) VALUES ($1, $2, $3, $4)"
                await self.db.execute(query, self.i.guild.id, self.i.channel_id, {}, [])
            await self.db.release(connection)
            query = "SELECT * FROM mangadex WHERE channel_id = $1 AND guild_id = $2"
            channel_exist = await self.bot.db.fetchrow(
                query, self.i.channel_id, self.i.guild.id
            )
        if not channel_exist.get("ignore_no_group", False):
            connection = await self.db.acquire()
            async with connection.transaction():
                query = f"UPDATE mangadex SET ignore_no_group = $1 WHERE guild_id = $2 AND channel_id = $3"
                await self.db.execute(query, [], self.i.guild.id, self.i.channel_id)  # type: ignore
            await self.db.release(connection)
        query = "SELECT * FROM mangadex WHERE channel_id = $1 AND guild_id = $2"
        channel_exist = await self.bot.db.fetchrow(
            query, self.i.channel_id, self.i.guild.id
        )
        return (json.loads(channel_exist["mangas"]), channel_exist["ignore_no_group"])  # type: ignore

    async def update(self, choice: int):
        res = await self.find_one()
        titles = self.info[0]
        manga_ids = self.info[1]
        if self.i.command.name == "add":
            if manga_ids[choice] not in res[0]:
                chapter_response: Optional[Chapter] = await self.md.get_latest(
                    manga_ids[choice]
                )
                title_response = chapter_response.get_title()
                latest = title_response[0]
                res[0].update({f"{manga_ids[choice]}": str(latest)})
                to_ignore = res[1]
                if self.ignore_individual:
                    to_ignore.append(manga_ids[choice])

                connection = await self.db.acquire()
                async with connection.transaction():
                    query = f"UPDATE mangadex SET mangas = $1, ignore_no_group = $2 WHERE guild_id = $3 AND channel_id = $4"
                    await self.db.execute(query, json.dumps(res[0]), to_ignore, self.i.guild.id, self.i.channel_id)  # type: ignore
                await self.db.release(connection)
                await self.i.channel.send(  # type: ignore
                    f"This channel will receive notifications on new chapters of {titles[choice]}, I suppose!"
                )
        else:
            if manga_ids[choice] in res[0]:
                res[0].pop(manga_ids[choice])
                connection = await self.db.acquire()
                async with connection.transaction():
                    query = f"UPDATE mangadex SET mangas = $1, WHERE guild_id = $2 AND channel_id = $3"
                    await self.db.execute(query, json.dumps(res[0]), self.i.guild.id, self.i.channel_id)  # type: ignore
                await self.db.release(connection)
                title = titles[choice]
                await self.i.channel.send(  # type: ignore
                    f"This channel will no longer receive notifications on new chapters of {title}, I suppose!"
                )

    @ui.button(
        emoji="1️⃣", style=discord.ButtonStyle.blurple, custom_id="persistent:one"
    )
    async def opt_one(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(0)

    @ui.button(
        emoji="2️⃣", style=discord.ButtonStyle.blurple, custom_id="persistent:two"
    )
    async def opt_two(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(1)

    @ui.button(
        emoji="3️⃣", style=discord.ButtonStyle.blurple, custom_id="persistent:three"
    )
    async def opt_three(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(2)

    @ui.button(
        emoji="4️⃣", style=discord.ButtonStyle.blurple, custom_id="persistent:four"
    )
    async def opt_four(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(3)

    @ui.button(
        emoji="5️⃣", style=discord.ButtonStyle.blurple, custom_id="persistent:five"
    )
    async def opt_five(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(4)

    @ui.select(
        placeholder="Select if you want to ignore individual translations or not.",
        options=[
            discord.SelectOption(value="0", label="Include"),
            discord.SelectOption(value="1", label="Ignore"),
        ],
    )
    async def choice(self, interaction: discord.Interaction, select: ui.Select[Self]):
        self.ignore_individual = select.values[0] == "1"
        await interaction.response.defer()
