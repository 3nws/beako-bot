import discord


async def commands_series(ctx):
    series = [
        "Kaguya-sama: Love is War (kaguya)",
        "Oshi no Ko (onk)",
        "Re:Zero (rz)",
        "Grand Blue Dreaming (gb)",
    ]
    frame = discord.Embed(
        color=discord.Colour.random()
    )
    counter = 1
    desc = ""
    for s in series:
        desc += f"**{counter}.** {s}\n"
        counter += 1
    frame.description = desc
    await ctx.send(embed=frame)
