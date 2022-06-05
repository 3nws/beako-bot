import discord
import random
import os
import json

from dotenv import load_dotenv      # type: ignore
from discord.ext import commands
from discord import app_commands
from aiohttp import ClientSession
from typing import Optional, Union
from Bot import Bot


load_dotenv()


class Gif(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.tenor_api_key = os.getenv('TENOR_API_KEY')


    @app_commands.command(name="pout")
    async def pout(self, i: discord.Interaction):
        """Send a pout gif.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
        """
        session: ClientSession = self.bot.session  
        async with session.get("https://g.tenor.com/v1/search?q=%s&key=%s" %
                               ("anime pout", self.tenor_api_key)) as r:
            if r.status == 200:
                response = await r.read()
                pouts = json.loads(response)
            else:
                print("Tenor down!")
                return
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        rand_index = random.randrange(len(pouts['results']))
        desc = '{} pouted, I suppose!'.format(i.user.mention)  
        embed = discord.Embed(description=desc, color=discord.Colour.random())
        embed.set_image(url=(pouts['results'])[rand_index]
                        ['media'][0]['mediumgif']['url'])
        await i.response.send_message(embed=embed)


    @app_commands.command(name="hug")
    @app_commands.describe(member="The member you want to hug, I suppose!")
    async def hug(self, i: discord.Interaction, member: Optional[Union[discord.Member, discord.User]]):
        """Hug someone.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member, optional): the member to ping. Defaults to None.
        """
        session: ClientSession = self.bot.session  
        async with session.get("https://g.tenor.com/v1/search?q=%s&key=%s" %
                                ("anime hug", self.tenor_api_key)) as r:
            if r.status == 200:
                response = await r.read()
                hugs = json.loads(response)
            else:
                print("Tenor down!")
                return
        if not member:
            member = i.user  
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        rand_index = random.randrange(len(hugs['results']))
        if i.user.id == member.id:  
            desc = 'Hugging yourself? Pathetic, I suppose!'
        elif member.id == self.bot.user.id:  
            desc = 'How dare you hug me, in fact?! *swoosh* Be gone, I suppose!'
        else:
            desc = '{} hugged {}, I suppose!'.format(
                i.user.mention, member.mention)  
        embed = discord.Embed(description=desc, color=discord.Colour.random())
        embed.set_image(url=(hugs['results'])[rand_index]
                        ['media'][0]['mediumgif']['url'])
        await i.response.send_message(embed=embed)


    @app_commands.command(name="smug")
    async def smug(self, i: discord.Interaction):
        """Be smug.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
        """
        session: ClientSession = self.bot.session  
        async with session.get("https://g.tenor.com/v1/search?q=%s&key=%s" %
                                ("anime smug", self.tenor_api_key)) as r:
            if r.status == 200:
                response = await r.read()
                smugs = json.loads(response)
            else:
                print("Tenor down!")
                return
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        rand_index = random.randrange(len(smugs['results']))
        desc = '{} is being smug, I suppose!'.format(i.user.mention)  
        embed = discord.Embed(description=desc, color=discord.Colour.random())
        embed.set_image(url=(smugs['results'])[rand_index]
                        ['media'][0]['mediumgif']['url'])
        await i.response.send_message(embed=embed)


    @app_commands.command(name="pat")
    @app_commands.describe(member="The member you want to pat, I suppose!")
    async def pat(self, i: discord.Interaction, member: Optional[Union[discord.Member, discord.User]]):
        """Pat someone that deserves it.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member, optional): the member to ping. Defaults to None.
        """
        session: ClientSession = self.bot.session  
        async with session.get("https://g.tenor.com/v1/search?q=%s&key=%s" %
                                ("anime pat", self.tenor_api_key)) as r:
            if r.status == 200:
                response = await r.read()
                pats = json.loads(response)
            else:
                print("Tenor down!")
                return
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        rand_index = random.randrange(len(pats['results']))
        if member is None:
            member = i.user  
        if i.user.id == member.id:  
            desc = 'Why are you patting yourself, I suppose!'
        elif member.id == self.bot.user.id:  
            desc = 'Don\'t get any funny ideas, Betty\'s trying to be nice so she\'ll allow it, in fact!'
        else:
            desc = '{} patted {}, I suppose!'.format(
                i.user.mention, member.mention)  
        embed = discord.Embed(description=desc, color=discord.Colour.random())
        embed.set_image(url=(pats['results'])[rand_index]
                        ['media'][0]['mediumgif']['url'])
        await i.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Gif(bot))
