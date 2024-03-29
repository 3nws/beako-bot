import discord
import random
import json

from discord.ext import commands
from discord import app_commands
from aiohttp import ClientSession
from typing import List, Optional

from Bot import Bot


class Fun(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.determine_flip = [1, 0]
        self.normal_API: str = (
            "https://normal-api.tk/image-search?redirect=false&query="
        )

    @app_commands.command(name="imagesearch")
    @app_commands.describe(query="What the image is going to be about, in fact!")
    async def image_api(self, i: discord.Interaction, *, query: str):
        """I'll send you an image. What it contains? IDK.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            query (str): the phrase to look for. Defaults to "".
        """
        await i.response.defer()
        session: ClientSession = self.bot.session
        async with session.get(self.normal_API + query) as r:
            if r.status == 200:
                response = await r.read()
                image: str = json.loads(response)["image"]
                embed = discord.Embed(colour=discord.Colour.random())
                embed.set_image(url=image)
                await i.followup.send(embed=embed)
            else:
                print("NormalAPI down!")
                embed = discord.Embed(
                    colour=discord.Colour.random(),
                    description="Something's wrong with the [Normal API](https://normal-api.tk/)",
                )
                await i.followup.send(embed=embed)

    @app_commands.command(name="say")
    @app_commands.describe(msg="The thing you want me to repeat, in fact!")
    async def say(self, i: discord.Interaction, *, msg: Optional[str]):
        """Make me repeat what you say.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            msg (str, optional): the phrase to repeat. Defaults to "".
        """
        if not msg:
            await i.response.send_message("What do you want me to say, in fact?!")
            return
        if random.randint(1, 100) % 2 == 0:
            await i.response.send_message(msg + ", in fact!")
        else:
            await i.response.send_message(msg + ", I suppose!")

    @app_commands.command(name="roll")
    @app_commands.describe(num="The upper limit for the roll, in fact!")
    async def roll(self, i: discord.Interaction, num: Optional[int]):
        """Roll a number.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            num (int, optional): upper limit for the roll. Defaults to None.
        """
        if num:
            number = random.randint(1, num)
        else:
            number = random.randint(1, 100)
        await i.response.send_message(
            f"{i.user.name} Just rolled **{number}**, I suppose!"
        )

    async def rps_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """An autocomplete function

        Args:
            interaction (discord.Interaction): the interaction that invokes this coroutine
            current (str): whatever the user has typed as the input

        Returns:
            List[app_commands.Choice[str]]: The list of choices matching the input
        """
        choices = ["Rock", "Paper", "Scissors"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices
            if current.lower() in choice.lower()
        ]

    @app_commands.command(name="rps")
    @app_commands.autocomplete(choice=rps_autocomplete)
    @app_commands.describe(choice="What do you want to draw against me, in fact?!")
    async def rps(self, i: discord.Interaction, choice: str):
        """Play rock paper scissors with me.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            choice (str): the choice the user makes
        """
        choice = choice.lower()
        if choice == "rock":
            counter = "paper"
        elif choice == "paper":
            counter = "scissors"
        else:
            counter = "rock"
        random_pick = random.randint(1, 3)

        if random_pick == 1:
            await i.response.send_message(
                f"HAHA! I win, I suppose! You stood no chance against my {counter}, in fact!"
            )
        elif random_pick == 2:
            await i.response.send_message(f"Well that's a draw, I suppose!")
        else:
            await i.response.send_message(
                f"Betty lost, I suppose! I knew I should have picked {counter}, in fact!"
            )

    @app_commands.command(name="coin")
    @app_commands.describe(
        heads="The thing that represents heads, I suppose!",
        tails="The thing that represents tails, I suppose!",
    )
    async def coinflip(
        self, i: discord.Interaction, heads: Optional[str], tails: Optional[str]
    ):
        """Throw a coin to decide.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            heads (str, optional): the result if heads faces up. Defaults to None.
            tails (str, optional): the result if tails faces up. Defaults to None.
        """
        if heads is not None and tails is None:
            embed = discord.Embed(
                title="Error",
                description=f"{i.user.mention} tried to flip a coin but didn't specify what for is tails, I suppose!",
            )
            await i.response.send_message(embed=embed)

        elif heads is None or tails is None:
            if random.choice(self.determine_flip) == 1:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{i.user.mention} flipped a coin, and got **Heads**, I suppose!",
                )
                await i.response.send_message(embed=embed)

            else:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{i.user.mention} flipped a coin, and got **Tails**, I suppose!",
                )
                await i.response.send_message(embed=embed)
        else:
            if random.choice(self.determine_flip) == 1:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{i.user.mention} flipped a coin, and got **Heads** for **{heads}**, I suppose!",
                )
                await i.response.send_message(embed=embed)

            else:
                embed = discord.Embed(
                    title="Coinflip",
                    description=f"{i.user.mention} flipped a coin, and got **Tails** for **{tails}**, I suppose!",
                )
                await i.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Fun(bot))
