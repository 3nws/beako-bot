import discord
import os
import dns
import asyncio
import logging
import threading
import typing
import pymongo

from dotenv import load_dotenv
from discord.ext import tasks, commands

# classes import
from Help import Help

# commands import
from commands.r_help import commands_help

logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(
#     filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter(
#     '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = pymongo.MongoClient('localhost', 27017)
        try:
            self.client.admin.command('ping')
        except ConnectionFailure:
            print("Local not available")
            self.client = pymongo.MongoClient(os.getenv("DB_URL"))

    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
            else:
                print(f'Unable to load {filename[:-3]}')

    def get_client(self):
        return self.client

bot = Bot(command_prefix="r.", intents=intents)
bot.remove_command("help")

# help command
@bot.tree.command(name='beakohelp', guild = None)
async def help(interaction: discord.Interaction):
    await commands_help(bot, interaction, Help())


# catch command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("What is that, I suppose?!\nTry `/beakohelp`, in fact!")

@bot.event
async def on_guild_join(guild):
    msg = f"Just joined {guild.name} with {guild.member_count} members, in fact!"
    user = bot.get_user(442715989310832650)
    await user.send(msg)
    print(msg)
    
@bot.event
async def on_guild_remove(guild):
    msg = f"Just left {guild.name}, in fact!\n\
            They didn't like Betty, I suppose!"
    user = bot.get_user(442715989310832650)
    await user.send(msg)
    print(msg)
    
# syncing slash commands
@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~"]] = None) -> None:
    if not guilds:
        if spec == "~":
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        else:
            fmt = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    fmt = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            fmt += 1

    await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")

# runs everytime the bot comes online
@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}\n')
    print(f'Server List ({len(bot.guilds)})\n')
    server_counter = 1
    for guild in set(bot.guilds):
        print(
            f"{server_counter}. {guild.name}, owned by {guild.owner} with {guild.member_count} members")
        server_counter += 1
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="/beakohelp and Songstress Liliana!"
        )
    )


async def main():
    async with bot:
        await bot.load_cogs()
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())
