import discord
import random

from discord.ext import commands
from random import choice


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.determine_flip = [1, 0]

    # beako will repeat what is passed in
    @commands.command()
    async def say(self, ctx, *, msg=""):
        await ctx.message.delete()
        if msg == "":
            await ctx.send("What do you want me to say, in fact?!")
            return
        if random.randint(1, 100) % 2 == 0:
            await ctx.send(msg + ", in fact!")
        else:
            await ctx.send(msg + ", I suppose!")

    # roll iq
    @commands.command()
    async def roll(self, ctx, num=""):
        if num.isnumeric():
            number = random.randint(1, int(num))
        else:
            number = random.randint(1, 100)
        await ctx.send(
            f"{ctx.message.author.name} Just rolled **{number}**, I suppose!"
        )

    # play rock paper scissors
    @commands.command()
    async def rps(self, ctx, choice):
        if choice == "rock":
            counter = "paper"
        elif choice == "paper":
            counter = "scissors"
        else:
            counter = "rock"

        random_pick = random.randint(1, 3)

        if random_pick == 1:
            await ctx.send(
                f"HAHA! I win, I suppose! You stood no chance against my {counter}, in fact!"
            )
        elif random_pick == 2:
            await ctx.send(f"Well that's a draw, I suppose!")
        else:
            await ctx.send(
                f"Betty lost, I suppose! I knew I should have picked {counter}, in fact!"
            )

    # coin flip
    @commands.command(aliases=["coin"])
    async def coinflip(self, ctx, heads=None, tails=None):
        if heads is not None and tails is None:
            embed = discord.Embed(
                title="Error",
                description=f"{ctx.author.mention} tried to flip a coin but didn't specify what for is tails, I suppose!",
            )
            await ctx.send(embed=embed)

        elif heads is None or tails is None:
            if random.choice(self.determine_flip) == 1:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{ctx.author.mention} flipped a coin, and got **Heads**, I suppose!",
                )
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{ctx.author.mention} flipped a coin, and got **Tails**, I suppose!",
                )
                await ctx.send(embed=embed)
        else:
            if random.choice(self.determine_flip) == 1:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{ctx.author.mention} flipped a coin, and got **Heads** for **{heads}**, I suppose!",
                )
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{ctx.author.mention} flipped a coin, and got **Tails** for **{tails}**, I suppose!",
                )
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
