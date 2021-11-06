from dotenv import load_dotenv
from pysaucenao import SauceNao

import os
import discord

load_dotenv()

saucenao_api_key = os.getenv('SAUCENAO_API_KEY')

saucenao = SauceNao(api_key=saucenao_api_key, results_limit=1)

async def commands_reverse_image_search(ctx, url):
    try:
        if url == "":
            await ctx.send("What image do you want to search for, I suppose?!")
            return
        sauce_frame = discord.Embed(
          color = discord.Colour.random()
        )
        results = await saucenao.from_url(url)
        best_result = results[0]
        sauce_frame.add_field(name=best_result.title+" by "+best_result.author_name+" with "+str(best_result.similarity)+" similarity", value=" on "+best_result.source_url)
        sauce_frame.set_image(url=best_result.thumbnail)
        await ctx.send(embed=sauce_frame)
    except:
        await ctx.send("That doesn't seem like a usable URL, in fact!")