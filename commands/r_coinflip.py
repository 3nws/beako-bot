import random
import discord

from random import choice

determine_flip = [1, 0]

async def commands_coinflip(ctx, heads, tails):
    if heads is not None and tails is None:
        embed = discord.Embed(title="Error", description=f"{ctx.author.mention} tried to flip a coin but didn't specify what for is tails, I suppose!")
        await ctx.send(embed=embed)
        
    elif heads is None or tails is None:
        if random.choice(determine_flip) == 1:
            embed = discord.Embed(title="Coinflip", description=f"{ctx.author.mention} flipped a coin, and got **Heads**, I suppose!")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Coinflip", description=f"{ctx.author.mention} flipped a coin, and got **Tails**, I suppose!")
            await ctx.send(embed=embed)
    else:
        if random.choice(determine_flip) == 1:
            embed = discord.Embed(title="Coinflip", description=f"{ctx.author.mention} flipped a coin, and got **Heads** for **{heads}**, I suppose!")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Coinflip", description=f"{ctx.author.mention} flipped a coin, and got **Tails** for **{tails}**, I suppose!")
            await ctx.send(embed=embed)