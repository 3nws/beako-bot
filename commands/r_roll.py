import random


async def commands_roll(ctx, num):
    if num.isnumeric():
        number = random.randint(1, int(num))
    else:
        number = random.randint(1, 100)
    await ctx.send(f"{ctx.message.author.name} Just rolled **{number}**, I suppose!")
