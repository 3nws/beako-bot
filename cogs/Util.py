import discord
import asyncio
import os

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

        # add 'db' parameter for specific databases
        self.saucenao = SauceNao(api_key=self.saucenao_api_key)

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
