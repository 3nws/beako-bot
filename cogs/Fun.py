import discord
import random

from discord.ext import commands
from discord import app_commands
from random import choice
from typing import List


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.determine_flip = [1, 0]

    # beako will repeat what is passed in
    @app_commands.command(name="say")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def say(self, i: discord.Interaction, *, msg:str=""):
        if (msg == ""):
            await i.response.send_message("What do you want me to say, in fact?!")
            return
        if random.randint(1, 100) % 2 == 0:
            await i.channel.send(msg + ", in fact!")
        else:
            await i.channel.send(msg + ", I suppose!")

    # roll iq
    @app_commands.command(name="roll")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def roll(self, i: discord.Interaction, num:str=""):
        if num.isnumeric():
            number = random.randint(1, int(num))
        else:
            number = random.randint(1, 100)
        await i.response.send_message(f"{i.user.name} Just rolled **{number}**, I suppose!")

    async def rps_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        choices = ['Rock', 'Paper', 'Scissors']
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if current.lower() in choice.lower()
        ]

    # play rock paper scissors
    @app_commands.command(name="rps")
    @app_commands.autocomplete(choices=rps_autocomplete)
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def rps(self, i: discord.Interaction, choices:str):
        choices = choices.lower()
        if (choices == 'rock'):
            counter = 'paper'
        elif (choices == 'paper'):
            counter = 'scissors'
        else:
            counter = 'rock'
        random_pick = random.randint(1, 3)

        if (random_pick == 1):
            await i.response.send_message(f"HAHA! I win, I suppose! You stood no chance against my {counter}, in fact!")
        elif (random_pick == 2):
            await i.response.send_message(f"Well that's a draw, I suppose!")
        else:
            await i.response.send_message(f"Betty lost, I suppose! I knew I should have picked {counter}, in fact!")
            

    # coin flip
    @app_commands.command(name="coin")
    @app_commands.guilds(discord.Object(id=658947832392187906))
    async def coinflip(self, i: discord.Interaction, heads:str=None, tails:str=None):
        if heads is not None and tails is None:
            embed = discord.Embed(
                title="Error", description=f"{i.user.mention} tried to flip a coin but didn't specify what for is tails, I suppose!")
            await i.response.send_message(embed=embed)

        elif heads is None or tails is None:
            if random.choice(self.determine_flip) == 1:
                embed = discord.Embed(
                    title="Coinflip", description=f"{i.user.mention} flipped a coin, and got **Heads**, I suppose!")
                await i.response.send_message(embed=embed)

            else:
                embed = discord.Embed(
                    title="Coinflip", description=f"{i.user.mention} flipped a coin, and got **Tails**, I suppose!")
                await i.response.send_message(embed=embed)
        else:
            if random.choice(self.determine_flip) == 1:
                embed = discord.Embed(
                    title="Coinflip", description=f"{i.user.mention} flipped a coin, and got **Heads** for **{heads}**, I suppose!")
                await i.response.send_message(embed=embed)

            else:
                embed = discord.Embed(
                    title="Coinflip", description=f"{i.user.mention} flipped a coin, and got **Tails** for **{tails}**, I suppose!")
                await i.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
