import discord
import json

from discord.ext import commands
from discord import app_commands
from aiohttp import ClientSession
from typing import List, Optional, Dict
from Bot import Bot


class Wordle(commands.Cog):    
    base_url: str = "https://word.digitalnook.net"
    status_colors: Dict[int, str] = {
        0: '⬛',
        1: '🟨',
        2: '🟩',
    }

    def __init__(self, bot: Bot):
        self.bot = bot
        self.key: str
        self.id: int
        self.i: discord.Interaction
        self.word_id: int
        self.embed: discord.Embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"\\_\\_\\_\\_\\_",
            )
        self.num_of_guesses: int = 0

    group = app_commands.Group(name="wordle", description="Wordle command group...")

    @group.command(name="start")
    async def start(self, i: discord.Interaction, word_id: Optional[int]) -> None:
        self.i = i
        session: ClientSession = self.bot.session
        async with session.post(f"{self.__class__.base_url}/api/v1/start_game/", data={"wordID": word_id}) as r:
            if r.status == 200:
                response = await r.read()
                response = json.loads(response)
                self.id = response['id']
                self.key = response['key']
                self.word_id = response['wordID']
            else:
                print("digitalnook down!")
                return
        self.embed.description = f"Word ID is '{self.id}', if you want to start again, in fact!"
        await i.response.send_message("The game has started, in fact! Start guessing with `/wordle guess`, I suppose!", embed=self.embed)
        


    @group.command(name="guess")
    @app_commands.describe(guess="Your guess for this wordle, I suppose!")
    async def guess(self, i: discord.Interaction, guess: str):
        self.num_of_guesses += 1
        new_state: str = ""
        guess_result: str = ""
        session: ClientSession = self.bot.session
        async with session.post(f"{self.__class__.base_url}/api/v1/guess/", json={
                                                                                "id": str(self.id),
                                                                                "key": self.key,
                                                                                "guess": guess,
                                                                                }) as r:
            if r.status == 200:
                response = await r.read()
                response = json.loads(response)
                temp: List[str] = []
                for l in response:
                    letter: str = l['letter']
                    status: str = self.__class__.status_colors[l['state']]
                    temp.append(f"{letter} - {status}")
                guess_result = ", ".join(temp)
                for result in temp:
                    result_list = result.split(' - ')
                    if result_list[1] == self.__class__.status_colors[2]:
                        new_state += result_list[0]
                    else:
                        new_state += "\\_"
            else:
                print("digitalnook down!")
                return
        
        self.embed.title = new_state
        if '_' not in new_state:
            await self.finish()
        else:
            await i.response.send_message(guess_result)
            await self.i.edit_original_message(content="The game has started, in fact! Start guessing with `/wordle guess`, I suppose!", embed=self.embed)

        if self.num_of_guesses >= 5:
            await self.finish()


    async def finish(self):
        answer: str = ""
        session: ClientSession = self.bot.session
        async with session.post(f"{self.__class__.base_url}/api/v1/guess/", data={
                                                                                "id": self.id,
                                                                                "key": self.key,
                                                                                }) as r:
            if r.status == 200:
                response = await r.read()
                response = json.loads(response)
                answer = response['anwswer']

        self.embed.title = answer
        await self.i.edit_original_message(content="The game has ended, in fact! Start another one with `/wordle start`, I suppose!", embed=self.embed)

async def setup(bot: Bot):
    await bot.add_cog(Wordle(bot))
