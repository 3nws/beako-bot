from dotenv import load_dotenv
from pysaucenao import SauceNao, PixivSource, GenericSource

# no idea why but I can't import TwitterSource class on the line above
import pysaucenao
TwitterSource = pysaucenao.containers.TwitterSource

import os
import discord

load_dotenv()

saucenao_api_key = os.getenv('SAUCENAO_API_KEY')

# add 'db' parameter for specific databases
saucenao = SauceNao(api_key=saucenao_api_key)

async def commands_reverse_image_search(ctx, url):
    try:
        if url == "":
            await ctx.send("What image do you want to search for, I suppose?!")
            return
        sauce_frame = discord.Embed(
          color = discord.Colour.random()
        )
        results = await saucenao.from_url(url)
        pixiv_result = ""
        twitter_result = ""
        for result in results:
            if isinstance(result, PixivSource):
                pixiv_result = result
            elif isinstance(result, TwitterSource):
                twitter_result = result
        if pixiv_result != "" and twitter_result != "":
            sauce_frame.add_field(name=f"{pixiv_result.title} by {pixiv_result.author_name} with {str(pixiv_result.similarity)} similarity",\
                             value=f"on [Pixiv]({pixiv_result.source_url}),\non [Twitter]({twitter_result.source_url})")
            sauce_frame.set_thumbnail(url=pixiv_result.thumbnail)
        elif pixiv_result == "" and twitter_result == "":
            sauce_frame = discord.Embed(title="No results!", description=f"I couldn't find that on pixiv or twitter, I suppose!")
        elif twitter_result == "":
            sauce_frame.add_field(name=f"{pixiv_result.title} by {pixiv_result.author_name} with {str(pixiv_result.similarity)} similarity",\
                             value=f"on [Pixiv]({pixiv_result.source_url})")
            sauce_frame.set_thumbnail(url=pixiv_result.thumbnail)
        else:
            sauce_frame.add_field(name=f"Image posted by {twitter_result.author_name} with {str(twitter_result.similarity)} similarity",\
                             value=f"on [Twitter]({twitter_result.source_url})")
            sauce_frame.set_thumbnail(url=twitter_result.thumbnail)

        await ctx.send(embed=sauce_frame)
    except:
        await ctx.send("It's not Betty's fault. Something went wrong, in fact!")