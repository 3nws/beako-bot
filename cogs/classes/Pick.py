import discord
import asyncio
import typing
import pymongo
import ast

from discord import ui
from commands.db.classes.MangaDex import MangaDex

class PickView(ui.View):
    
    def __init__(self, i: discord.Interaction, channels: pymongo.collection.Collection, info):
        super().__init__(timeout=60)
        self.i: discord.Interaction = i
        self.channels: pymongo.collection.Collection = channels
        self.mangas: dict = {}
        self.md: MangaDex = MangaDex()
        self.info: tuple = info
        self.num_of_results: int = len(self.info[0])
        if self.num_of_results != len(self._children):
            for j in range(len(self._children)-1, self.num_of_results-1, -1):
                self.remove_item(self._children[j])
        
        
    async def on_timeout(self):
        self.stop()
        await self.msg.edit(content=self.text, embed=self.embed, view=self.disabled())
        await self.msg.reply("This view just timed out, I suppose! You need to interact with it to keep it up, in fact!")
        
    async def interaction_check(self, interaction):
        return interaction.user == self.i.user
    
    async def find_one(self):
        channel_exist = await self.channels.find_one(
                        {
                        "channel_id": self.i.channel_id,
                        "guild_id": self.i.guild.id,
                        }
                    )
        if not channel_exist:
            channel_exist = await self.channels.insert_one({
                'channel_id': self.i.channel_id,
                "guild_id": self.i.guild.id,
                'mangas': '{}',
            })
            channel_exist = await self.channels.find_one(
                        {
                        "channel_id": self.i.channel_id,
                        "guild_id": self.i.guild.id,
                        }
                    )
        return ast.literal_eval(channel_exist['mangas'])
    
    async def update(self, choice: int):
        res = await self.find_one()
        titles = self.info[0]
        manga_ids = self.info[1]
        if manga_ids[choice] not in res:
            chapter_response = await self.md.get_latest(manga_ids[choice])
            title_response = chapter_response.get_title()
            latest = title_response[0]
            is_title = title_response[1]
            chapter_link = chapter_response.get_link()
            res.update({f"{manga_ids[choice]}": str(latest)})
            new_doc = await self.channels.find_one_and_update(
                {
                    'channel_id': self.i.channel_id,
                    "guild_id": self.i.guild.id,
                    },
                {
                    '$set': {
                        'mangas': str(res)
                    }
                },
                return_document=pymongo.ReturnDocument.AFTER
            )
            await self.i.channel.send(f"This channel will receive notifications on new chapters of {titles[choice]}, I suppose!")
        
    @ui.button(emoji='1️⃣', style=discord.ButtonStyle.blurple)
    async def opt_one(self, interaction, button):
        await interaction.response.defer()
        await self.update(0)
        
    @ui.button(emoji='2️⃣', style=discord.ButtonStyle.blurple)
    async def opt_two(self, interaction, button):
        await interaction.response.defer()
        await self.update(1)
        
    @ui.button(emoji='3️⃣', style=discord.ButtonStyle.blurple)
    async def opt_three(self, interaction, button):
        await interaction.response.defer()
        await self.update(2)
        
    @ui.button(emoji='4️⃣', style=discord.ButtonStyle.blurple)
    async def opt_four(self, interaction, button):
        await interaction.response.defer()
        await self.update(3)
        
    @ui.button(emoji='5️⃣', style=discord.ButtonStyle.blurple)
    async def opt_five(self, interaction, button):
        await interaction.response.defer()
        await self.update(4)
        
        