import random


async def commands_say(ctx, msg):
    await ctx.message.delete()
    if (msg == ""):
        await ctx.send("What do you want me to say, in fact?!")
        return
    if random.randint(1, 100) % 2 == 0:
        await ctx.send(msg+", in fact!")
    else:
        await ctx.send(msg+", I suppose!")
