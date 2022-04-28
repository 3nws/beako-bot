import discord
import asyncio
import os
import requests

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from pysaucenao import SauceNao, PixivSource, GenericSource

# no idea why but I can't import TwitterSource class on the line above
import pysaucenao

load_dotenv()


class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.TwitterSource = pysaucenao.containers.TwitterSource
        self.saucenao_api_key = os.getenv('SAUCENAO_API_KEY')
        self.TOKEN = os.getenv('TOKEN')

        # add 'db' parameter for specific databases
        self.saucenao = SauceNao(api_key=self.saucenao_api_key)

    # send available series
    @app_commands.command(name="series")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def series(self, i: discord.Interaction):
        series = {
            "Kaguya-sama: Love is War (kaguya)",
            "Oshi no Ko (onk)",
            "Re:Zero (rz)",
            "Grand Blue Dreaming (gb)",
        }
        frame = discord.Embed(
            color=discord.Colour.random()
        )
        counter = 1
        desc = ""
        for s in series:
            desc += f"**{counter}.** {s}\n"
            counter += 1
        frame.description = desc
        await i.response.send_message(embed=frame)

    # sends a user's avatar
    @app_commands.command(name="avatar")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def avatar(self, i: discord.Interaction, member: discord.Member = None):
        avatar_frame = discord.Embed(
            color=discord.Colour.random()
        )
        if member:
            avatar_frame.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s avatar, I suppose!")
            avatar_frame.set_image(url=f'{member.avatar.url}')
        else:
            avatar_frame.add_field(
                name=str(i.user) + " requested", value=" their own avatar, I suppose!")
            avatar_frame.set_image(url=f'{i.user.avatar.url}')

        await i.response.send_message(embed=avatar_frame)
        
    # sends a user's server avatar
    @app_commands.command(name="savatar")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def server_avatar(self, i: discord.Interaction, member: discord.Member = None):
        avatar_frame = discord.Embed(
            color=discord.Colour.random()
        )
        if member:
            if member.display_avatar is None:
                return await self.avatar(i, member)
            avatar_frame.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s avatar, I suppose!")
            avatar_frame.set_image(url=f'{member.display_avatar.url}')
        else:
            if i.user.display_avatar is None:
                return await self.avatar(i, member)
            avatar_frame.add_field(
                name=str(i.user) + " requested", value=" their own avatar, I suppose!")
            avatar_frame.set_image(url=f'{i.user.display_avatar.url}')

        await i.response.send_message(embed=avatar_frame)

    # sends a user's banner
    @app_commands.command(name="banner")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def banner(self, i: discord.Interaction, member: discord.Member = None):
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        image_size = '?size=1024'
        member = i.user if not member else member
        base_url = 'https://discord.com/api'
        users_endpoint = f'/users/{member.id}'
        headers = {'Authorization': f'Bot {self.TOKEN}'}
        s = requests.Session()
        r = s.get(f'{base_url}{users_endpoint}', headers=headers)
        banner_hash = r.json()['banner']
        if banner_hash:
            animated = banner_hash.startswith('a_')
            file_extension = 'gif' if animated else 'png'
        else:
            file_extension = 'png'
        image_base_url = 'https://cdn.discordapp.com/'
        banners_endpoint = f'banners/{member.id}/{banner_hash}.{file_extension}'
        r = f'{image_base_url}{banners_endpoint}{image_size}'

        if f'None.{file_extension}' in r:
            embed.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s banner, I suppose! Shame they don't have any, in fact!")
        elif member != i.user:
            embed.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s banner, I suppose!")
            embed.set_image(url=f'{r}')
        else:
            embed.add_field(
                name=str(i.user) + " requested", value=" their own banner, I suppose!")
            embed.set_image(url=f'{r}')

        await i.response.send_message(embed=embed)

    # reverse search image
    @app_commands.command(name="sauce")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def reverse_image_search(self, i: discord.Interaction, url:str=""):
        try:
            if url == "":
                await i.response.send_message("What image do you want to search for, I suppose?!")
                return
            sauce_frame = discord.Embed(
                color=discord.Colour.random()
            )
            results = await self.saucenao.from_url(url)
            pixiv_result = ""
            twitter_result = ""
            for result in results:
                if isinstance(result, PixivSource):
                    pixiv_result = result
                elif isinstance(result, self.TwitterSource):
                    twitter_result = result
            if pixiv_result != "" and twitter_result != "":
                sauce_frame.add_field(name=f"{pixiv_result.title} by {pixiv_result.author_name} with {str(pixiv_result.similarity)} similarity",
                                      value=f"on [Pixiv]({pixiv_result.source_url}),\non [Twitter]({twitter_result.source_url})")
                sauce_frame.set_thumbnail(url=pixiv_result.thumbnail)
            elif pixiv_result == "" and twitter_result == "":
                sauce_frame = discord.Embed(
                    title="No results!", description=f"I couldn't find that on pixiv or twitter, I suppose!")
            elif twitter_result == "":
                sauce_frame.add_field(name=f"{pixiv_result.title} by {pixiv_result.author_name} with {str(pixiv_result.similarity)} similarity",
                                      value=f"on [Pixiv]({pixiv_result.source_url})")
                sauce_frame.set_thumbnail(url=pixiv_result.thumbnail)
            else:
                sauce_frame.add_field(name=f"Image posted by {twitter_result.author_name} with {str(twitter_result.similarity)} similarity",
                                      value=f"on [Twitter]({twitter_result.source_url})")
                sauce_frame.set_thumbnail(url=twitter_result.thumbnail)

            sauce_frame.set_footer(
                text=f"on {str(i.user)}'s request, I suppose!", icon_url=i.user.avatar.url)

            await i.response.send_message(embed=sauce_frame)
        except BaseException:
            await i.response.send_message("It's not Betty's fault. Something went wrong, in fact!")

    # creates a poll with two choices
    @app_commands.command(name="poll")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def poll(self, i: discord.Interaction, c1:str, c2:str, *, question:str=""):
        embed = discord.Embed(
            title=question.upper(),
            description=f":one: {c1}\n\n:two: {c2}\n",
            color=discord.Colour.random(),
        )

        embed.set_footer(
            text=f"Poll created by {i.user.nick}", icon_url=i.user.avatar.url)

        msg = await i.channel.send(embed=embed)

        emojis = ['1️⃣', '2️⃣']

        for emoji in emojis:
            await msg.add_reaction(emoji)

        await i.response.send_message("I'll be back with the results in three minutes, I suppose!")
        
        await asyncio.sleep(180)

        message_1 = await i.channel.fetch_message(msg.id)

        reactions = {react.emoji: react.count for react in message_1.reactions}

        results = discord.Embed(
            title="Results",
            description=f"{c1}: {reactions[emojis[0]]}\n\n{c2}: {reactions[emojis[1]]}",
            color=discord.Colour.random()
        )

        results.set_footer(
            text=f"For the poll '{question}'", icon_url=i.user.avatar.url)

        await i.channel.send(embed=results)


async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
