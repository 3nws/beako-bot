import asyncio
import discord
import os

from discord.app_commands import AppCommand
from dotenv import load_dotenv  # type: ignore
from discord.ext import commands
from typing import List, Literal, Optional

from Bot import MyTree, Bot, Help


# logging.basicConfig(level=logging.INFO)

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


client = discord.Client(intents=intents)
tree = MyTree(client)
bot = Bot(
    command_prefix="r.",  # type: ignore
    intents=intents,  # type: ignore
    tree_cls=MyTree,  # type: ignore
    help_command=None,  # type: ignore
    activity=discord.Activity(  # type: ignore
        type=discord.ActivityType.listening, name="/beakohelp and Songstress Liliana!"
    ),
)


@bot.tree.command(name="beakohelp", guild=None)
async def help(interaction: discord.Interaction):
    await Help(bot).get_help(interaction)


@bot.event
async def on_command_error(ctx: commands.Context[Bot], error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("What is that, I suppose?!\nTry `/beakohelp`, in fact!")
    else:
        print(error)


@bot.event
async def on_guild_join(guild: discord.Guild):
    msg = f"Just joined {guild.name} with {guild.member_count} members, in fact!"
    user = bot.get_user(442715989310832650)
    await user.send(msg)
    print(msg)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    msg = f"Just left {guild.name}, in fact!\nThey didn't like Betty, I suppose!"
    user = bot.get_user(442715989310832650)
    await user.send(msg)
    print(msg)


@bot.command()
@commands.is_owner()
async def sync(
    ctx: commands.Context[Bot],
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~"]],
) -> None:
    if not guilds:
        if spec == "~":
            fmt: List[AppCommand] = await ctx.bot.tree.sync(guild=ctx.guild)
        else:
            fmt: List[AppCommand] = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    fmt_i: int = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            fmt_i += 1

    await ctx.send(f"Synced the tree to {fmt_i}/{len(guilds)} guilds.")


@bot.command()
@commands.is_owner()
async def getcount(ctx):
    await ctx.send(ctx.bot.tree.app_commands_invoked)
    messages: List[str] = []
    for cmd, user, namespace in ctx.bot.tree.app_command_invokes_namespaces:
        messages.append(f"{user} used {cmd} with {namespace}.")

    if len(messages) < 10 and len(messages) > 0:
        return await ctx.send("\n".join(messages))
    elif len(messages) > 0:
        for i in range(len(messages) // 10 + 1):
            if (i + 1) * 10 > len(messages):
                return await ctx.send("\n".join(messages[i * 10 : len(messages)]))
            await ctx.send("\n".join(messages[i * 10 : (i + 1) * 10]))
            await asyncio.sleep(1)


@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}\n")


def main():
    bot.run(os.getenv("TOKEN", "no"))


if __name__ == "__main__":
    main()
