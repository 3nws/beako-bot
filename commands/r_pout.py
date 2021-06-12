import random
import os
import requests
import json
import discord

from dotenv import load_dotenv

load_dotenv()

async def commands_pout(ctx):
    apikey = os.getenv('TENOR_API_KEY')
    r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s" % ("anime pout", apikey))
    if r.status_code == 200:
        pouts = json.loads(r.content)
    embed = discord.Embed(
        color = discord.Colour.random()
    )
    rand_index=random.randrange(len(pouts['results']))
    desc = '{} pouted.'.format(ctx.author.mention)
    embed = discord.Embed(description=desc, color = discord.Colour.random())
    embed.set_image(url=(pouts['results'])[rand_index]['media'][0]['mediumgif']['url'])
    await ctx.send(embed=embed)