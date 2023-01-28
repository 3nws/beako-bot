import asyncio
import discord
import os
import asyncpg
import logging

from discord.app_commands import AppCommand
from dotenv import load_dotenv  # type: ignore
from discord.ext import commands
from typing import List, Literal, Optional, Dict

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

    if len(messages) < 5 and len(messages) > 0:
        return await ctx.send("\n".join(messages))
    elif len(messages) > 0:
        for i in range(len(messages) // 5 + 1):
            if (i + 1) * 5 > len(messages):
                return await ctx.send("\n".join(messages[i * 5 : len(messages)]))
            await ctx.send("\n".join(messages[i * 5 : (i + 1) * 5]))
            await asyncio.sleep(1)


@bot.command()
@commands.is_owner()
async def getstats(ctx):
    stats: Dict[str, int] = {}

    for tup in ctx.bot.tree.app_command_invokes_namespaces:
        command_name = tup[0]
        if stats.get(command_name, None):
            stats[command_name] += 1
        else:
            stats[command_name] = 1
    stats = dict(sorted(stats.items(), key=lambda item: item[1], reverse=True))
    embed = discord.Embed(
        title="Stats",
        colour=discord.Colour.random(),
        description="\n".join([f"{k}: {v}" for k, v in stats.items()]),
    )
    await ctx.send(embed=embed)


def error_handler(task: asyncio.Task):
    exc = task.exception()
    if exc:
        logging.error("ready task failed!", exc_info=exc)


async def run_once_when_ready():
    await bot.wait_until_ready()
    cog = bot.get_cog("DB")
    # cog.tasks_change_avatar.start()  # type: ignore
    cog.tasks_check_chapter.start()  # type: ignore
    address = ["0.0.0.0"]
    while True:
        if bot.no_client:
            client, address = await bot.loop.sock_accept(bot.server)
            bot.no_client = False
        await asyncio.sleep(1)
        if address[0] != os.getenv("ADMIN_IP", None):
            try:
                client.close()  # type: ignore
            except Exception:
                pass
            finally:
                bot.no_client = True
                continue
        bot.loop.create_task(bot.handle_client(client))  # type: ignore
        bot.loop.create_task(bot.send_stats(client))  # type: ignore


@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}\n")


async def main():
    async with bot:
        credentials = {
            "user": os.getenv("DB_USERNAME"),
            "password": os.getenv("DB_PASSWORD"),
            "database": "beako",
            "host": "127.0.0.1",
            "port": "5432",
        }
        db = await asyncpg.create_pool(**credentials)

        await db.execute(
            "CREATE TABLE IF NOT EXISTS tags(guild_id bigint PRIMARY KEY NOT NULL, tags json);"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS flips(id serial PRIMARY KEY, url text);"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS avatars(id serial PRIMARY KEY, url text);"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS chapter_ex(id serial PRIMARY KEY NOT NULL, title text);"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS channel(id serial PRIMARY KEY NOT NULL, guild_id bigint NOT NULL, series_id bigint NOT NULL);"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS mangadex(id serial PRIMARY KEY NOT NULL, guild_id bigint NOT NULL, channel_id bigint NOT NULL, mangas json, ignore_no_group text[]);"
        )
        bot.db = db
        ready_task = asyncio.create_task(run_once_when_ready())
        ready_task.add_done_callback(error_handler)
        await bot.start(os.getenv("TOKEN_DEBUG", "no"))


if __name__ == "__main__":
    asyncio.run(main())
