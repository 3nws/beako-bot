import discord
import asyncio
import os
import json

from discord.ext import commands
from discord import app_commands
from aiohttp import ClientSession
from dotenv import load_dotenv  # type: ignore
from pysaucenao import SauceNao, PixivSource, TwitterSource  # type: ignore
from pysaucenao.containers import SauceNaoResults
from typing import Optional, Any, Dict


load_dotenv()


class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.saucenao_api_key = os.getenv('SAUCENAO_API_KEY')
        self.TOKEN = os.getenv('TOKEN')

        # add 'db' parameter for specific databases
        self.saucenao: SauceNao = SauceNao(api_key=self.saucenao_api_key)


    @app_commands.command(name="series")
    async def series(self, i: discord.Interaction):
        """Get the legacy series information.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
        """
        series = {
            "Kaguya-sama: Love is War (kaguya)",
            "Oshi no Ko (onk)",
            "Re:Zero (rz)",
            "Grand Blue Dreaming (gb)",
            "Any series on MangaDex. See `/manga, /add, /remove`"
        }
        frame = discord.Embed(
            color=discord.Colour.random()
        )
        counter = 1
        desc = ""
        for s in series:
            desc += f"**{counter}.** {s}\n"
            counter += 1
        frame.description = desc  # type: ignore
        await i.response.send_message(embed=frame)


    @app_commands.command(name="avatar")
    @app_commands.describe(member="The member you want to ~~steal~~borrow their avatar from, in fact!")
    async def avatar(self, i: discord.Interaction, member: Optional[discord.Member]):
        """Get a member's avatar.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member, optional): the member to take avatar from. Defaults to None.
        """
        avatar_frame = discord.Embed(
            color=discord.Colour.random()
        )
        if member:
            avatar_frame.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s avatar, I suppose!")  # type: ignore
            avatar_frame.set_image(url=f'{member.avatar.url}')  # type: ignore
        else:
            avatar_frame.add_field(
                name=str(i.user) + " requested", value=" their own avatar, I suppose!")  # type: ignore
            avatar_frame.set_image(url=f'{i.user.avatar.url}')  # type: ignore

        await i.response.send_message(embed=avatar_frame)
        

    @app_commands.command(name="savatar")
    @app_commands.describe(member="The member you want to ~~steal~~borrow their server specific avatar from, in fact!")
    async def server_avatar(self, i: discord.Interaction, member: Optional[discord.Member]) -> Any:
        """Get the member's server specific avatar.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member, optional): the member to take server specific avatar from. Defaults to None.

        Returns:
            None: None
        """
        avatar_frame = discord.Embed(
            color=discord.Colour.random()
        )
        if member:
            if member.display_avatar is None:
                return await self.avatar(i, member)  # type: ignore
            avatar_frame.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s server avatar, I suppose!")  # type: ignore
            avatar_frame.set_image(url=f'{member.display_avatar.url}')
        else:
            if i.user.display_avatar is None:  # type: ignore
                return await self.avatar(i, member)  # type: ignore
            avatar_frame.add_field(
                name=str(i.user) + " requested", value=" their own server avatar, I suppose!")  # type: ignore
            avatar_frame.set_image(url=f'{i.user.display_avatar.url}')  # type: ignore

        await i.response.send_message(embed=avatar_frame)


    @app_commands.command(name="banner")
    @app_commands.describe(member="The member you want to ~~steal~~borrow their banner from, in fact!")
    async def banner(self, i: discord.Interaction, member: Optional[discord.Member]):
        """Get the member's banner.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member, optional): the member to take the banner from. Defaults to None.
        """
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        image_size = '?size=1024'
        member = i.user if not member else member  # type: ignore
        base_url = 'https://discord.com/api'
        users_endpoint = f'/users/{member.id}'  # type: ignore
        headers = {'Authorization': f'Bot {self.TOKEN}'}
        session: ClientSession = self.bot.session  # type: ignore
        async with session.get(f'{base_url}{users_endpoint}', headers=headers) as r:
            if r.status == 200:
                response = await r.read()
                r = json.loads(response)
            else:
                print("Something went wrong with the Discord API request!")
                return
        banner_hash = r['banner']
        if banner_hash:
            animated = banner_hash.startswith('a_')
            file_extension = 'gif' if animated else 'png'
        else:
            file_extension = 'png'
        image_base_url = 'https://cdn.discordapp.com/'
        banners_endpoint = f'banners/{member.id}/{banner_hash}.{file_extension}'  # type: ignore
        r = f'{image_base_url}{banners_endpoint}{image_size}'

        if f'None.{file_extension}' in r:
            embed.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s banner, I suppose! Shame they don't have any, in fact!")  # type: ignore
        elif member != i.user:  # type: ignore
            embed.add_field(name=str(
                i.user) + " requested", value=member.mention + "'s banner, I suppose!")  # type: ignore
            embed.set_image(url=f'{r}')
        else:
            embed.add_field(
                name=str(i.user) + " requested", value=" their own banner, I suppose!")  # type: ignore
            embed.set_image(url=f'{r}')

        await i.response.send_message(embed=embed)


    sauce_group = app_commands.Group(name="sauce", description="Sauce command group...")


    async def send_sauce(self, i: discord.Interaction, url: str):
        """Sends an embed with the source information of the image.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            url (str): url of the image
        """
        try:
            sauce_frame = discord.Embed(
                color=discord.Colour.random()
            )
            results: SauceNaoResults = await self.saucenao.from_url(url)  # type: ignore
            pixiv_result = ""
            twitter_result = ""
            for result in results:  # type: ignore
                if isinstance(result, PixivSource):
                    pixiv_result = result  # type: ignore
                elif isinstance(result, TwitterSource):  # type: ignore
                    twitter_result = result  # type: ignore
            if pixiv_result != "" and twitter_result != "":
                sauce_frame.add_field(name=f"{pixiv_result.title} by {pixiv_result.author_name} with {str(pixiv_result.similarity)} similarity",  # type: ignore
                                      value=f"on [Pixiv]({pixiv_result.source_url}),\non [Twitter]({twitter_result.source_url})")  # type: ignore
                sauce_frame.set_thumbnail(url=pixiv_result.thumbnail)  # type: ignore
            elif pixiv_result == "" and twitter_result == "":
                sauce_frame = discord.Embed(
                    title="No results!", description=f"I couldn't find that on pixiv or twitter, I suppose!")
            elif twitter_result == "":
                sauce_frame.add_field(name=f"{pixiv_result.title} by {pixiv_result.author_name} with {str(pixiv_result.similarity)} similarity",  # type: ignore
                                      value=f"on [Pixiv]({pixiv_result.source_url})")  # type: ignore
                sauce_frame.set_thumbnail(url=pixiv_result.thumbnail)  # type: ignore
            else:
                sauce_frame.add_field(name=f"Image posted by {twitter_result.author_name} with {str(twitter_result.similarity)} similarity",  # type: ignore
                                      value=f"on [Twitter]({twitter_result.source_url})")  # type: ignore
                sauce_frame.set_thumbnail(url=twitter_result.thumbnail)  # type: ignore

            sauce_frame.set_footer(
                text=f"on {str(i.user)}'s request, I suppose!", icon_url=i.user.avatar.url)  # type: ignore

            await i.response.send_message(embed=sauce_frame)
        except BaseException:
            await i.response.send_message("It's not Betty's fault. Something went wrong, in fact!")


    @sauce_group.command(name="url")
    @app_commands.describe(url="The url of the image you want to find the source of, in fact!")
    async def reverse_image_search_w_url(self, i: discord.Interaction, url: str):
        """Find the source of the image by url.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            url (str): url of the image
        """
        await self.send_sauce(i, url)


    @sauce_group.command(name="file")
    @app_commands.describe(file="The image file you want to find the source of, in fact!")
    async def reverse_image_search_w_file(self, i: discord.Interaction, file: discord.Attachment):
        """Find the source of the image by uploading it.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            file (discord.Attachment): image file
        """
        await self.send_sauce(i, file.url)  # type: ignore


    @app_commands.command(name="poll")
    @app_commands.describe(c1="First choice, in fact!", c2="Second choice, in fact!", question="The question this poll is for, in fact!")
    async def poll(self, i: discord.Interaction, c1: str, c2: str, *, question: str=""):
        """Create a poll.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            c1 (str): first choice of the poll
            c2 (str): second choice of the poll
            question (str, optional): question this poll is trying to answer. Defaults to "".
        """
        embed = discord.Embed(
            title=question.upper(),
            description=f":one: {c1}\n\n:two: {c2}\n",
            color=discord.Colour.random(),
        )

        embed.set_footer(
            text=f"Poll created by {i.user.nick}", icon_url=i.user.avatar.url)  # type: ignore

        msg: discord.Message = await i.channel.send(embed=embed)  # type: ignore

        emojis = ['1️⃣', '2️⃣']

        for emoji in emojis:
            await msg.add_reaction(emoji)

        await i.response.send_message("I'll be back with the results in three minutes, I suppose!")
        
        await asyncio.sleep(180)

        message_1: discord.Message = await i.channel.fetch_message(msg.id)  # type: ignore

        reactions: Dict[Any, Any] = {react.emoji: react.count for react in message_1.reactions}  # type: ignore

        results = discord.Embed(
            title="Results",
            description=f"{c1}: {reactions[emojis[0]]}\n\n{c2}: {reactions[emojis[1]]}",
            color=discord.Colour.random()
        )

        results.set_footer(
            text=f"For the poll '{question}'", icon_url=i.user.avatar.url)  # type: ignore

        await i.channel.send(embed=results)  # type: ignore


async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
