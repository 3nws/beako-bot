import discord

from discord.ext import commands
from discord import app_commands
from typing import List, Optional


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


    @app_commands.command(name="kick")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(member="The user you want to kick, in fact!", reason="The reason for this kick, I suppose!")
    async def kick(self, i: discord.Interaction, member: discord.Member, *, reason: Optional[str]):
        """Yeet a member from this server.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member): the member to yeet
            reason (str, optional): the reason this member was yeeted. Defaults to None.

        Returns:
            _type_: _description_
        """
        if member.top_role > i.member.top_role:  # type: ignore
            return await i.response.send_message(f"You can't kick this person, I suppose!")
        await member.kick(reason=reason)
        return await i.response.send_message(f"{member} has been yeeted, I suppose!")


    @app_commands.command(name="ban")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The user you want to ban, in fact!", reason="The reason for this ban, I suppose!")
    async def ban(self, i: discord.Interaction, member: discord.Member, *, reason: Optional[str]):
        """Ban a member from this server.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member): the member to ban
            reason (str, optional): the reason this member was banned. Defaults to None.

        Returns:
            _type_: _description_
        """
        if member.top_role > i.member.top_role:  # type: ignore
            return await i.response.send_message(f"You can't ban this person, I suppose!")
        await member.ban(reason=reason)
        await i.response.send_message(f"{member} has been yeeted forever, I suppose!")
        

    @app_commands.command(name="unban")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(user="The user you want to unyeet, in fact!")
    async def unban(self, i: discord.Interaction, *, user: discord.User):
        """Unban a user on this server.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            user (discord.User): the user to unban
        """
        await i.guild.unban(user)  # type: ignore
        await i.response.send_message(f"{user} has been unbanned, I suppose!")


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
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(limit="Amount of messages you want to delete, in fact!", direction="In which direction you want to start deleting, I suppose?!",
                           msg_id="The message id you want to start deleting from, in fact!")
    async def clean(self, i: discord.Interaction, limit: int, direction: Optional[str], msg_id: Optional[str]):
        """Clean this channel's messages.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            limit (int): the number of messages to delete
            direction (str, optional): the direction to delete towards. Defaults to None.
            msg_id (str, optional): the message id to start deleting from. Defaults to None.

        Returns:
            None: None
        """
        if direction:
            direction = self.dir_aliases[direction] if direction in self.dir_aliases else direction
            direction = direction.lower()
        await i.response.defer()
        original = await i.original_message()
        if (msg_id):
            msg: discord.Message = await i.channel.fetch_message(int(msg_id))  # type: ignore
            if direction == "after":
                await i.channel.purge(limit=limit+1, bulk=True, after=msg, oldest_first=True, check=lambda m: m.id != original.id)  # type: ignore
            elif direction == "before":
                await i.channel.purge(limit=limit+1, bulk=True, before=msg, oldest_first=False, check=lambda m: m.id != original.id)  # type: ignore
        elif (direction == "after"):
            return await i.response.send_message("I can't delete future messages, in fact! Tell me which message you want me to start deleting from, I suppose!")
        else:
            await i.channel.purge(limit=limit+1, bulk=True, check=lambda m: m.id != original.id)  # type: ignore
        await i.followup.send(content='Cleared by {}, I suppose!'.format(i.user.mention))  # type: ignore


    @app_commands.command(name="purge")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(member="The member you want to delete the messages of, in fact!")
    async def purge(self, i: discord.Interaction, member: Optional[discord.Member]):
        """Purge a member's messages .

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            member (discord.Member, optional): the member to purge messages of. Defaults to None.
        """
        if member == self.bot.user:
            await i.response.send_message("Nope, in fact!")
        elif member:
            async for message in i.channel.history(oldest_first=False):  # type: ignore
                if message.author == member:  # type: ignore
                    await message.delete()  # type: ignore
            await i.response.send_message(f'I have cleansed this channel of {member.mention}\'s messages, in fact!')
        else:
            await i.response.send_message("Which degenerate's messages do you want to yeet, I suppose?!")


    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx: commands.Context[discord.Message]):
        """Send a list of servers and some info about this bot.

        Args:
            ctx (commands.Bot.Context): the context for this command
        """
        msg = f'Logged in as: {self.bot.user.name}\n'  # type: ignore
        msg += f'Server List ({len(self.bot.guilds)})\n'
        server_counter = 1
        for guild in set(self.bot.guilds):
            msg += f"{server_counter}. {guild.name}, owned by {guild.owner} with {guild.member_count} members\n"  # type: ignore
            server_counter += 1
        await ctx.send(msg)  # type: ignore

    
    @commands.command(aliases=["kill"])
    @commands.is_owner()
    async def terminate(self, ctx: commands.Context[discord.Message]):
        """Terminate or restart the bot.

        Args:
            ctx (commands.Bot.Context): the context for this command
        """
        await ctx.send("Betty goes offline, I suppose!")
        await self.bot.close()


    @commands.command()
    @commands.is_owner()
    async def toggle(self, ctx: commands.Context[discord.Message], cmd):  # type: ignore
        """Toggles commands on and off.

        Args:
            ctx (commands.Bot.Context): the context for this command
            cmd (str): the command to toggle
        """
        cmd = self.bot.get_command(cmd)  # type: ignore

        if ctx.command == cmd:  # type: ignore
            await ctx.reply("Wait, that's illegal, I suppose!")
        else:
            cmd.enabled = not cmd.enabled  # type: ignore
            status = "enabled" if cmd.enabled else "disabled"  # type: ignore
            await ctx.send(f"I have {status} the `{cmd.qualified_name}` command, in fact!")  # type: ignore


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
