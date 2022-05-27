import discord

from discord.ext import commands
from discord import app_commands
from typing import List, Optional
from io import BytesIO


class Tag(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = self.bot.get_client()
        db_tags = self.client.tags
        self.tags_coll = db_tags.data
        self.tags_list = {}
        
    
    async def sync_tags(self, guild_id):
        self.tags_list = await self.tags_coll.find_one({
            "guild_id": guild_id, 
        })
        self.tags_list = self.tags_list['tags'] if self.tags_list is not None and 'tags' in self.tags_list.keys() else {}
         
    
    group = app_commands.Group(name="tag", description="Tag command group...")
        
        
    async def tag_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        await self.sync_tags(interaction.guild.id)
        return [
            app_commands.Choice(name=tag, value=tag)
            for tag in self.tags_list if current.lower() in tag or current.lower() in self.tags_list[tag]
        ][:25]
    
    
    @group.command(name="show")
    @app_commands.guild_only
    @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.describe(tag_name="The name for this tag, I suppose! So you can find its contents later, in fact!")
    async def get_tag(self, i: discord.Interaction, *, tag_name:str):
        await i.response.defer()
        try:
            await i.followup.send(self.tags_list[tag_name])
        except Exception as e:
            content = self.tags_list[tag_name]
            if isinstance(content, bytes):
                buffer = BytesIO(content)
                file = discord.File(buffer, filename='image.png')
                return await i.followup.send(file=file)
            buffer = BytesIO(content.encode('utf-8'))
            file = discord.File(buffer, filename='text.md')
            await i.followup.send(file=file)
            
        
    @group.command(name="add")
    @app_commands.guild_only
    @app_commands.describe(tag_name="The soon to be added tag's name, in fact!", tag_content="Contents of this tag, I suppose!",
                           tag_file="You can also pass a file as the tag's contents, in fact! It will override the previous argument, in fact!")
    async def add_tag(self, i: discord.Interaction, tag_name: str, tag_content: Optional[str], tag_file: Optional[discord.Attachment]):
        if tag_file is not None:
            data = await tag_file.read()
            try:
                tag_content = data.decode('ascii')
            except UnicodeDecodeError:
                tag_content = data
        if tag_content is None:
            return await i.response.send_message("What should this tag return, in fact!")
        await self.sync_tags(i.guild.id)
        new = False
        if self.tags_list != {}:
            self.tags_list[tag_name] = tag_content
        if self.tags_list == {}:
            self.tags_list = {
                "guild_id": i.guild.id,
                "tags": {
                    tag_name: tag_content,
                }
            }
            await self.tags_coll.insert_one(self.tags_list)
            new = True
        if not new:
            await self.tags_coll.find_one_and_update(
                                    {
                                        'guild_id': i.guild.id,
                                        },
                                    {
                                        '$set': {
                                            'tags': self.tags_list,
                                        }
                                    }
                                )
        await i.response.send_message("Tag added, in fact!")
        
        
    @group.command(name="remove")
    @app_commands.guild_only
    @app_commands.autocomplete(tag_name=tag_autocomplete)
    @app_commands.describe(tag_name="The tag you want to remove, I suppose!")
    async def remove_tag(self, i: discord.Interaction, tag_name:str):
        await self.sync_tags(i.guild.id)
        self.tags_list.pop(tag_name)
        await self.tags_coll.find_one_and_update(
                                {
                                    'guild_id': i.guild.id,
                                    },
                                {
                                    '$set': {
                                        'tags': self.tags_list,
                                    }
                                }
                            )
        await i.response.send_message("Tag removed, in fact!")
     
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Tag(bot))
