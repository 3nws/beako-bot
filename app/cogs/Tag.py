import discord
import json

from discord.ext import commands
from discord import app_commands
from typing import List, Any, Dict, Mapping
from pymongo.collection import Collection
from io import BytesIO
from classes.Views.AddTagModal import AddTagModal

from Bot import Bot


class Tag(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.tags_list: Dict[int, Dict[str, Any]] = {}

    async def sync_tags(self):
        """Sync the tags according to guilds."""
        query = "SELECT * FROM tags"
        rows = await self.bot.db.fetch(query)
        for row in rows:
            self.tags_list[row["guild_id"]] = json.loads(row["tags"])

    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:
        await self.sync_tags()

    group = app_commands.Group(
        name="tag", description="Tag command group...", guild_only=True
    )

    async def tag_autocomplete(
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
            app_commands.Choice(name=tag, value=tag)
            for tag in self.tags_list[interaction.guild_id]  # type: ignore
            if current.lower() in tag
            or (
                isinstance(self.tags_list[interaction.guild_id][tag], str)  # type: ignore
                and current.lower() in self.tags_list[interaction.guild_id][tag]  # type: ignore
            )
        ][:25]

    @group.command(name="show")
    @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.describe(
        tag_name="The name for this tag, I suppose! So you can find its contents later, in fact!"
    )
    async def get_tag(self, i: discord.Interaction, tag_name: str):
        """Get the given tag's content.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            tag_name (str): the tag name to look up

        Returns:
            None: None
        """
        await i.response.defer()
        try:
            await i.followup.send(self.tags_list[i.guild_id][tag_name])  # type: ignore
        except Exception as e:
            print(e)
            content = self.tags_list[i.guild_id][tag_name]  # type: ignore
            if isinstance(content, bytes):
                buffer = BytesIO(content)
                file = discord.File(buffer, filename="image.png")
                return await i.followup.send(file=file)
            buffer = BytesIO(content.encode("utf-8"))
            file = discord.File(buffer, filename="text.md")
            await i.followup.send(file=file)

    @group.command(name="add")
    # @app_commands.describe(
    #     tag_name="The soon to be added or edited tag's name, in fact!",
    #     tag_content="Contents of this tag, I suppose!",
    #     #    tag_file="You can also pass a file as the tag's contents, in fact! It will override the previous argument, in fact!"
    # )
    # @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_tag(
        self,
        i: discord.Interaction,
        #  tag_file: Optional[discord.Attachment]
    ):
        """Add or edit a tag on this server. This will send a form.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine

        Returns:
            None: None
        """
        await i.response.send_modal(AddTagModal(self, self.bot))

    @group.command(name="remove")
    @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.describe(tag_name="The tag you want to remove, I suppose!")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove_tag(self, i: discord.Interaction, tag_name: str):
        """Remove a tag from this guild.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            tag_name (str): the name of the tag to delete
        """
        self.tags_list[i.guild_id].pop(tag_name)  # type: ignore
        connection = await self.bot.db.acquire()
        async with connection.transaction():
            query = f"UPDATE tags SET tags = $1 WHERE guild_id = $2"
            await self.bot.db.execute(query, json.dumps(self.tags_list[i.guild_id]), i.guild_id)  # type: ignore
        await self.bot.db.release(connection)
        await i.response.send_message("Tag removed, in fact!")


async def setup(bot: Bot):
    await bot.add_cog(Tag(bot))
