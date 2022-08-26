import async_google_trans_new
import discord

from discord.ext import commands
from discord import app_commands
from typing import List

from Bot import Bot


class TL(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.g = async_google_trans_new.AsyncTranslator()  # type: ignore
        self.is_synced = False
        self.langs: List[str] = list(async_google_trans_new.constant.LANGUAGES.values())  # type: ignore

    async def lang_autocomplete(
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
        return [
            app_commands.Choice(name=lang, value=lang)
            for lang in self.langs
            if current.lower() in lang.lower()
        ][:25]

    @app_commands.command(name="translate")
    @app_commands.autocomplete(language=lang_autocomplete)
    @app_commands.describe(
        text="The text you want to translate, in fact!",
        language="The language you want to translate to, I suppose!",
    )
    async def translate(self, i: discord.Interaction, text: str, language: str):
        """Translate a phrase to wished language.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            text (str): the phrase to translate
            language (str): the languate to translate it to
        """
        await i.response.defer()
        detected: str = (await self.g.detect(text))[1].capitalize()  # type: ignore
        lang_code: str = [
            s
            for s in async_google_trans_new.constant.LANGUAGES  # type: ignore
            if async_google_trans_new.constant.LANGUAGES[s] == language  # type: ignore
        ][0]
        res: str = (await self.g.translate(text, lang_code)).strip()  # type: ignore
        language = language.capitalize()
        await i.followup.send(
            f'"{text}" ({detected}) translates to "{res}" in {language}, in fact!'
        )


async def setup(bot: Bot):
    await bot.add_cog(TL(bot))
