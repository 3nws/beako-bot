import discord

from discord.ext import commands
from discord import app_commands
from discord import Permissions
from typing import List


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dir_aliases = {
            'b': 'before',
            'up': 'before',
            'u': 'before',
            'a': 'after',
            'down': 'after',
            'd': 'after',
        }

    # kicks member
    @app_commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(user="The user you want to kick, in fact!", reason="The reason for this kick, I suppose!")
    async def kick(self, i: discord.Interaction, user: discord.Member, *, reason: str = None):
        if user.top_role > i.user.top_role:
            return await i.response.send_message(f"You can't kick this person, I suppose!")
        await user.kick(reason=reason)
        return await i.response.send_message(f"{user} has been yeeted, I suppose!")

    # bans member
    @app_commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(user="The user you want to ban, in fact!", reason="The reason for this ban, I suppose!")
    async def ban(self, i: discord.Interaction, user: discord.Member, *, reason: str = None):
        if user.top_role > i.user.top_role:
            return await i.response.send_message(f"You can't ban this person, I suppose!")
        await user.ban(reason=reason)
        await i.response.send_message(f"{user} has been yeeted forever, I suppose!")

    @kick.error
    async def kick_error(self, error, ctx):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to do that, I suppose!")

    @ban.error
    async def ban_error(self, error, ctx):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to do that, I suppose!")

    # unbans user
    @app_commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(user="The user you want to unyeet, in fact!")
    async def unban(self, i: discord.Interaction, *, user: discord.User):
        await i.guild.unban(user)
        await i.response.send_message(f"{user} has been unbanned, I suppose!")

    @unban.error
    async def unban_error(self, error, ctx):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to do that, I suppose!")

    async def clean_autocomplete(self,
                                 interaction: discord.Interaction,
                                 current: str,
                                 ) -> List[app_commands.Choice[str]]:
        directions = ['Before', 'After']
        return [
            app_commands.Choice(name=direction, value=direction)
            for direction in directions if current.lower() in direction.lower()
        ]


    @app_commands.command(name="clean")
    @app_commands.autocomplete(direction=clean_autocomplete)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(limit="Amount of messages you want to delete, in fact!", direction="In which direction you want to start deleting, I suppose?!",
                           msg_id="The message id you want to start deleting from, in fact!")
    async def clean(self, i: discord.Interaction, limit: int, direction: str = None, msg_id: str = None):
        direction = self.dir_aliases[direction] if direction in self.dir_aliases else direction
        if direction is not None:
            direction = direction.lower()
        await i.response.defer()
        original = await i.original_message()
        if (msg_id):
            msg = await i.channel.fetch_message(int(msg_id))
            if direction == "after":
                await i.channel.purge(limit=limit+1, bulk=True, after=msg, oldest_first=True, check=lambda m: m.id != original.id)
            elif direction == "before":
                await i.channel.purge(limit=limit+1, bulk=True, before=msg, oldest_first=False, check=lambda m: m.id != original.id)
        elif (direction == "after"):
            return await i.response.send_message("I can't delete future messages, in fact! Tell me which message you want me to start deleting from, I suppose!")
        else:
            await i.channel.purge(limit=limit+1, bulk=True, check=lambda m: m.id != original.id)
        await i.followup.send(content='Cleared by {}, I suppose!'.format(i.user.mention))


    @app_commands.command(name="purge")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(member="The member you want to delete the messages of, in fact!")
    async def purge(self, i: discord.Interaction, member: discord.Member = None):
        if member == self.bot.user:
            await i.response.send_message("Nope, in fact!")
        elif member:
            async for message in i.channel.history(oldest_first=False):
                if message.author == member:
                    await message.delete()
            await i.response.send_message(f'I have cleansed this channel of {member.mention}\'s messages, in fact!')
        else:
            await i.response.send_message("Which degenerate's messages do you want to yeet, I suppose?!")


    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        msg = f'Logged in as: {self.bot.user.name}\n'
        msg += f'Server List ({len(self.bot.guilds)})\n'
        server_counter = 1
        for guild in set(self.bot.guilds):
            msg += f"{server_counter}. {guild.name}, owned by {guild.owner} with {guild.member_count} members\n"
            server_counter += 1
        await ctx.send(msg)

    
    @commands.command(aliases=["kill"])
    @commands.is_owner()
    async def terminate(self, ctx):
        await ctx.send("Betty goes offline, I suppose!")
        await self.bot.close()


    @commands.command()
    @commands.is_owner()
    async def toggle(self, ctx, cmd):
        cmd = self.bot.get_command(cmd)

        if ctx.command == cmd:
            await ctx.reply("Wait, that's illegal, I suppose!")
        else:
            cmd.enabled = not cmd.enabled
            status = "enabled" if cmd.enabled else "disabled"
            await ctx.send(f"I have {status} the `{cmd.qualified_name}` command, in fact!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
