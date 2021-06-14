import random
import os
import requests
import json
import discord

from dotenv import load_dotenv

load_dotenv()
tenor_api_key = os.getenv('TENOR_API_KEY')

async def commands_pout(ctx):
    r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s" % ("anime pout", tenor_api_key))
    if r.status_code == 200:
        pouts = json.loads(r.content)
    embed = discord.Embed(
        color = discord.Colour.random()
    )
    rand_index=random.randrange(len(pouts['results']))
    desc = '{} pouted, I suppose!'.format(ctx.author.mention)
    embed = discord.Embed(description=desc, color = discord.Colour.random())
    embed.set_image(url=(pouts['results'])[rand_index]['media'][0]['mediumgif']['url'])
    await ctx.send(embed=embed)
    
async def commands_pat(ctx, user):
    r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s" % ("anime pat", tenor_api_key))
    if not user:
        user = ctx.author
    if r.status_code == 200:
        pats = json.loads(r.content)
    embed = discord.Embed(
        color = discord.Colour.random()
    )
    rand_index=random.randrange(len(pats['results']))
    if ctx.author.id == user.id:
        desc = 'Why are you patting yourself, I suppose!'
    else:
        desc = '{} patted {}, I suppose!'.format(ctx.author.mention, user.mention)
    embed = discord.Embed(description=desc, color = discord.Colour.random())
    embed.set_image(url=(pats['results'])[rand_index]['media'][0]['mediumgif']['url'])
    await ctx.send(embed=embed)