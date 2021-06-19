import random
import discord

from random import choice

determine_flip = [1, 0]

async def commands_coinflip(ctx):
    if random.choice(determine_flip) == 1:
        embed = discord.Embed(title="Coinflip", description=f"{ctx.author.mention} flipped a coin, and got **Heads**, I suppose!")
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title="Coinflip", description=f"{ctx.author.mention} flipped a coin, and got **Tails**, I suppose!")
        await ctx.send(embed=embed)