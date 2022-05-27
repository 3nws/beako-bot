import discord
import asyncio
import typing

from discord import ui


class Pick(ui.View):
    
    def __init__(self):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.i: discord.Interaction = None
        self.msg: discord.Message = None
        self.embed: discord.Embed = None
        self.text: str = None
        self.group: str = None
        
    async def on_timeout(self):
        self.stop()
        await self.msg.edit(content=self.text, embed=self.embed, view=self.disabled())
        await self.msg.reply("This view just timed out, I suppose! You need to interact with it to keep it up, in fact!")