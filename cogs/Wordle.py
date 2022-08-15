import discord
import json

from discord.ext import commands
from discord import app_commands
from aiohttp import ClientSession
from typing import List, Optional, Dict, Any, ClassVar
from Bot import Bot


class Wordle(commands.Cog):
    base_url: ClassVar[str] = "https://word.digitalnook.net"
    status_colors: ClassVar[Dict[int, str]] = {
        0: "⬛",
        1: "🟨",
        2: "🟩",
    }

    def __init__(self, bot: Bot):
        self.bot = bot
        self.key: str
        self.id: int = -1
        self.word_id: int
        self.games: Dict[int, Any] = {}

    group: ClassVar[app_commands.Group] = app_commands.Group(name="wordle", description="Wordle command group...")

    @group.command(name="start")
    async def start(self, i: discord.Interaction, word_id: Optional[int]) -> None:
        """Start a wordle game.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            word_id (Optional[int]): optional word id
        """
        session: ClientSession = self.bot.session
        async with session.post(
            f"{self.__class__.base_url}/api/v1/start_game/", data={"wordID": word_id}
        ) as r:
            if r.status == 200:
                response = await r.read()
                response = json.loads(response)
                self.id = response["id"]
                self.key = response["key"]
                self.word_id = response["wordID"]
            else:
                print("digitalnook down!")
                return
        embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"-----",
        )
        embed.description = (
            f"Word ID is '{self.id}', if you want to start again, in fact!"
        )
        self.games[i.user.id] = {
            "num_of_guesses": 0,
            "guessed_words": [],
            "interaction": i,
            "embed": embed,
        }
        await i.response.send_message(
            "The game has started, in fact! Start guessing with `/wordle guess`, I suppose!",
            embed=embed,
            ephemeral=True,
        )

    @group.command(name="guess")
    @app_commands.describe(guess="Your guess for this wordle, I suppose!")
    async def guess(self, i: discord.Interaction, guess: str):
        """Make your guess for the current game.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            guess (str): user's guess
        """
        if self.games == {} or i.user.id not in self.games:
            return await i.response.send_message(
                "You have not started a game yet, in fact! Try `/wordle start` first, I suppose!",
                ephemeral=True,
            )
        if len(guess) != 5:
            return await i.response.send_message(
                "That word is not five letters length, in fact!", ephemeral=True
            )
        if guess in self.games[i.user.id]["guessed_words"]:
            return await i.response.send_message(
                "You have already tried that word, in fact!", ephemeral=True
            )
        new_state: str = ""
        guess_result: str = ""
        session: ClientSession = self.bot.session
        async with session.post(
            f"{self.__class__.base_url}/api/v1/guess/",
            json={
                "id": str(self.id),
                "key": self.key,
                "guess": guess,
            },
        ) as r:
            if r.status == 200:
                response = await r.read()
                response = json.loads(response)
                temp: List[str] = []
                for l in response:
                    letter: str = l["letter"]
                    status: str = self.__class__.status_colors[l["state"]]
                    temp.append(f"{letter} - {status}")
                guess_result = " | ".join(temp)
                for result in temp:
                    result_list = result.split(" - ")
                    if result_list[1] == self.__class__.status_colors[2]:
                        new_state += result_list[0]
                    else:
                        new_state += "-"
            else:
                return await i.response.send_message(
                    "Not a valid word, I suppose!", ephemeral=True
                )
        self.games[i.user.id]["num_of_guesses"] += 1
        self.games[i.user.id]["guessed_words"].append(guess)
        temp2: str = ""
        for j, c in enumerate(new_state):
            if self.games[i.user.id]["embed"].title is not None:
                if self.games[i.user.id]["embed"].title[j] != "-":
                    temp2 += self.games[i.user.id]["embed"].title[j]
                else:
                    temp2 += c
        self.games[i.user.id]["embed"].title = temp2
        if "-" not in new_state:
            await self.finish(self.games[i.user.id]["interaction"])
        else:
            await i.response.send_message(guess_result, ephemeral=True)
            await self.games[i.user.id]["interaction"].edit_original_message(
                content="The game has started, in fact! Start guessing with `/wordle guess`, I suppose!",
                embed=self.games[i.user.id]["embed"],
            )

        if self.games[i.user.id]["num_of_guesses"] >= 5:
            await self.finish(self.games[i.user.id]["interaction"])

    def reset_game(self, i: discord.Interaction):
        del self.games[i.user.id]

    async def finish(self, i: discord.Interaction):
        answer: str = ""
        session: ClientSession = self.bot.session
        async with session.post(
            f"{self.__class__.base_url}/api/v1/guess/",
            data={
                "id": self.id,
                "key": self.key,
            },
        ) as r:
            if r.status == 200:
                response = await r.read()
                response = json.loads(response)
                answer = response["answer"]
        win: bool = False
        if self.games[i.user.id]["embed"].title == answer:
            win = True
        self.games[i.user.id]["embed"].title = answer
        await i.edit_original_message(
            content="The game has ended, in fact! Start another one with `/wordle start`, I suppose!",
            embed=self.games[i.user.id]["embed"],
        )
        self.reset_game(i)
        if win:
            await i.followup.send(
                "You have finished the wordle successfully, in fact!", ephemeral=True
            )
        else:
            await i.followup.send("Better luck next time, I suppose!", ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Wordle(bot))
