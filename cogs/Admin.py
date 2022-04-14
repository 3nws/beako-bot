import discord

from discord.ext import commands
from discord import Permissions

class Admin(commands.Cog):
    def __init__(self, bot):
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
    @commands.command(aliases=["yeet", "yeeto"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        if user.top_role > ctx.author.top_role:
            return await ctx.send(f"You can't kick this person, I suppose!")
        await user.kick(reason=reason)
        return await ctx.send(f"{user} has been yeeted, I suppose!")
    
    # bans member
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        if user.top_role > ctx.author.top_role:
            return await ctx.send(f"You can't ban this person, I suppose!")
        await user.ban(reason=reason)
        await ctx.send(f"{user} has been yeeted forever, I suppose!")

    @kick.error
    async def kick_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have permission to do that, I suppose!")
            
    @ban.error
    async def ban_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have permission to do that, I suppose!")

    # unbans user
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in set(banned_users):
            user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user} has been unbanned, I suppose!")
            return
        
    @unban.error
    async def unban_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send("You don't have permission to do that, I suppose!")

    # clears chat
    @commands.command(aliases=["clear"])
    @commands.has_permissions(administrator=True)
    async def clean(self, ctx, limit: int, direction: str=None, msg_id: int=None):
        await ctx.message.delete()
        direction = self.dir_aliases[direction] if direction in self.dir_aliases else direction

        if (msg_id):
            msg = await ctx.fetch_message(msg_id)
            if direction == "after":
                history = await ctx.channel.history(limit=limit, after=msg, oldest_first=True).flatten()
            elif direction == "before":
                history = await ctx.channel.history(limit=limit, before=msg, oldest_first=False).flatten()
            for message in set(history):
                await message.delete()
        elif (direction == "after"):
            return await ctx.send("I can't delete future messages, in fact! Tell me which message you want me to start deleting from, I suppose!")
        elif (direction == "before"):
            history = await ctx.channel.history(limit=limit, before=ctx.message, oldest_first=False).flatten()
            for message in set(history):
                await message.delete()
        else:
            await ctx.channel.purge(limit=limit)

        await ctx.send('Cleared by {}, I suppose!'.format(ctx.author.mention))
        
    # deletes a member's all messages
    @commands.command(aliases=["cleanse"])
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, member: discord.Member=None):
        if member == self.bot.user:
            await ctx.send("Nope, in fact!")
        elif member:
            async for message in ctx.channel.history(oldest_first=False):
                if message.author == member:
                    await message.delete()
            await ctx.send(f'I have cleansed this channel of {member.mention}\'s messages, in fact!')
        else:
            await ctx.send("Which degenerate's messages do you want to yeet, I suppose?!")

    # print the joined servers in the logs
    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        print(f'Logged in as: {self.bot.user.name}\n')
        print(f'Server List ({len(self.bot.guilds)})\n')
        server_counter = 1
        for guild in set(self.bot.guilds):
            print(f"{server_counter}. {guild.name}, owned by {guild.owner} with {guild.member_count} members")
            server_counter += 1

    # terminates the bot
    @commands.command(aliases=["kill"])
    @commands.is_owner()
    async def terminate(self, ctx):
        await ctx.send("Betty goes offline, I suppose!")
        await self.bot.close()
        
    # toggles commands
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
        


def setup(bot):
    bot.add_cog(Admin(bot))
