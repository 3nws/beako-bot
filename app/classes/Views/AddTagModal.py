import discord
import json

from discord.ext import commands

import traceback

from Bot import Bot

# class TagDropdown(discord.ui.Select):

#     def __init__(self, modal, cog, name, content, **kwargs):
#         super().__init__(**kwargs)
#         self.modal = modal
#         self.cog = cog
#         self.name = name
#         self.content = content

#     async def callback(self, interaction: discord.Interaction) -> Any:
#         print(interaction.data)
#         # self.name.value = self.cog.tags_list[interaction.guild_id][interaction.data]


class AddTagModal(discord.ui.Modal, title="Add a Tag"):
    name = discord.ui.TextInput(
        label="Tag name",
        placeholder="Tag name here...",
    )
    content = discord.ui.TextInput(
        label="Tag content",
        style=discord.TextStyle.long,
        placeholder="Tag content here...",
        max_length=500,
    )

    def __init__(self, cog: commands.Cog, bot: Bot) -> None:
        super().__init__()
        self.cog = cog
        self.bot = bot
        self.db = bot.db
        # tags = [discord.SelectOption(label="Existing tags for this server...", value="None", default=True)] + ([discord.SelectOption(label=tag, value=tag) for tag in self.cog.tags_list[guild_id].keys()])  # type: ignore
        # # tags = TagDropdown(self, self.cog, self.name, self.content, options=tags[:25])
        # tags = discord.ui.Select(options=tags[:25])
        # self.add_item(tags)

    async def on_submit(self, interaction: discord.Interaction):
        msg: str = "Tag added, in fact!"
        # if tag_file is not None:
        #     data = await tag_file.read()
        #     if sys.getsizeof(data)//(1024*1024) > 4:
        #         return await i.followup.send("Wow! That's too large, I suppose! Keep it below 4MB, in fact!")
        #     try:
        #         self.content.value = data.decode('ascii')
        #     except UnicodeDecodeError:
        #         self.content.value = data
        if self.content.value is None:
            return await interaction.response.send_message(
                "What should this tag return, in fact!"
            )
        if self.name.value in self.cog.tags_list[interaction.guild.id]:  # type: ignore
            msg = "Tag edited, in fact!"
        new = False
        if self.cog.tags_list != {}:  # type: ignore
            self.cog.tags_list[interaction.guild_id][self.name.value] = self.content.value  # type: ignore
        if self.cog.tags_list == {}:  # type: ignore
            to_insert = {
                self.name.value: self.content.value,
            }
            connection = await self.db.acquire()
            async with connection.transaction():
                query = "INSERT INTO tags (guild_id, tags) VALUES ($1, $2)"
                await self.db.execute(
                    query, interaction.guild.id, json.dumps(to_insert)
                )
            await self.db.release(connection)
            new = True
        if not new:
            connection = await self.db.acquire()
            async with connection.transaction():
                query = f"UPDATE tags SET tags = $1 WHERE guild_id = $2"
                await self.db.execute(query, json.dumps(self.cog.tags_list[interaction.guild_id]), interaction.guild.id)  # type: ignore
            await self.db.release(connection)
        await interaction.response.send_message(msg)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        traceback.print_tb(error.__traceback__)
