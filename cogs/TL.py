import async_google_trans_new
import discord

from discord.ext import commands
from discord import app_commands
from typing import List


class TL(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.g = async_google_trans_new.AsyncTranslator()
        self.is_synced = False
        self.langs = list(async_google_trans_new.constant.LANGUAGES.values())

    
    async def lang_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=lang, value=lang)
            for lang in self.langs if current.lower() in lang.lower()
        ][:25]
    
    
    @app_commands.command(name="translate")
    @app_commands.autocomplete(language=lang_autocomplete)
    @app_commands.describe(text="The text you want to translate, in fact!", language="The language you want to translate to, I suppose!")
    async def translate(self, i: discord.Interaction, text: str, language: str):
        await i.response.defer()
        detected = (await self.g.detect(text))[1].capitalize()
        lang_code = [s for s in async_google_trans_new.constant.LANGUAGES if async_google_trans_new.constant.LANGUAGES[s]==language][0]
        res = (await self.g.translate(text, lang_code)).strip()
        language = language.capitalize()
        await i.followup.send(f'"{text}" ({detected}) translates to "{res}" in {language}, in fact!')
        

async def setup(bot: commands.Bot):
    await bot.add_cog(TL(bot))
