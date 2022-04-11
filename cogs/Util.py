import discord
import asyncio
import os
import requests

from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
from pysaucenao import SauceNao, PixivSource, GenericSource

# no idea why but I can't import TwitterSource class on the line above
import pysaucenao

load_dotenv()


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TwitterSource = pysaucenao.containers.TwitterSource
        self.saucenao_api_key = os.getenv('SAUCENAO_API_KEY')
        self.TOKEN = os.getenv('TOKEN')

        # add 'db' parameter for specific databases
        self.saucenao = SauceNao(api_key=self.saucenao_api_key)

    # send available series
    @commands.command()
    async def series(self, ctx):
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
        await ctx.send(embed=frame)

    # sends a user's avatar
    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        avatar_frame = discord.Embed(
            color=discord.Colour.random()
        )
        if member:
            avatar_frame.add_field(name=str(
                ctx.author)+" requested", value=member.mention+"'s avatar, I suppose!")
            avatar_frame.set_image(url=f'{member.avatar_url}')
        else:
            avatar_frame.add_field(
                name=str(ctx.author)+" requested", value=" their own avatar, I suppose!")
            avatar_frame.set_image(url=f'{ctx.author.avatar_url}')

        await ctx.send(embed=avatar_frame)
        
    # sends a user's banner
    @commands.command()
    async def banner(self, ctx, member: discord.Member = None):
        embed = discord.Embed(
            color=discord.Colour.random()
        )
        image_size = '?size=1024'
        member = ctx.author if not member else member
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
                ctx.author)+" requested", value=member.mention+"'s banner, I suppose! Shame they don't have any, in fact!")
        elif member != ctx.author:
            embed.add_field(name=str(
                ctx.author)+" requested", value=member.mention+"'s banner, I suppose!")
            embed.set_image(url=f'{r}')
        else:
            embed.add_field(
                name=str(ctx.author)+" requested", value=" their own banner, I suppose!")
            embed.set_image(url=f'{r}')
            
        await ctx.send(embed=embed)
        
    # reverse search image
    @commands.command(aliases=["ris", "sauce", "source"])
    async def reverse_image_search(self, ctx, url=""):
            try:
                if url == "":
                    await ctx.send("What image do you want to search for, I suppose?!")
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
                    text=f"on {str(ctx.author)}'s request, I suppose!", icon_url=ctx.author.avatar_url)

                await ctx.send(embed=sauce_frame, reference=ctx.message)
            except:
                await ctx.send("It's not Betty's fault. Something went wrong, in fact!", reference=ctx.message)

            await ctx.message.delete()
             
    # creates a poll with two choices
    @commands.command()
    async def poll(self, ctx, c1, c2, *, question=""):
        embed = discord.Embed(
            title=question.upper(),
            description=f":one: {c1}\n\n:two: {c2}\n",
            color=discord.Colour.random(),
        )

        embed.set_footer(
            text=f"Poll created by {ctx.author.nick}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)

        emojis = ['1️⃣', '2️⃣']

        for emoji in emojis:
            await msg.add_reaction(emoji)

        await asyncio.sleep(180)

        message_1 = await ctx.channel.fetch_message(msg.id)

        reactions = {react.emoji: react.count for react in message_1.reactions}

        results = discord.Embed(
            title="Results",
            description=f"{c1}: {reactions[emojis[0]]}\n\n{c2}: {reactions[emojis[1]]}",
            color=discord.Colour.random()
        )

        results.set_footer(
            text=f"For the poll '{question}'", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=results)

def setup(bot):
    bot.add_cog(Util(bot))
