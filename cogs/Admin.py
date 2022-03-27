import discord

from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # kicks member
    @commands.command(aliases=["yeet", "yeeto"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        await user.kick(reason=reason)
        await ctx.send(f"{user} has been yeeted, I suppose!")
    
    # bans member
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        await user.ban(reason=reason)
        await ctx.send(f"{user} has been yeeted forever, I suppose!")

    # unbans user
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user} has been unbanned, I suppose!")
            return

    # clears chat
    @commands.command(aliases=["clear"])
    @commands.has_permissions(administrator=True)
    async def clean(self, ctx, limit: int, msg_id=None):
        await ctx.message.delete()

        if (msg_id):
            msg = await ctx.fetch_message(msg_id)
            history = await ctx.channel.history(limit=limit, after=msg, oldest_first=True).flatten()
            for message in history:
                await message.delete()
        else:
            await ctx.channel.purge(limit=limit)

        await ctx.send('Cleared by {}, I suppose!'.format(ctx.author.mention))

    # print the joined servers in the logs
    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        print(f'Logged in as: {self.bot.user.name}\n')
        print(f'Server List ({len(self.bot.guilds)})\n')
        server_counter = 1
        for guild in self.bot.guilds:
            print(f"{server_counter}. {guild.name}, owned by {guild.owner} with {guild.member_count} members")
            server_counter += 1



def setup(bot):
    bot.add_cog(Admin(bot))
