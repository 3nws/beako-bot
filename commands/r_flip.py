import random

async def commands_flip(ctx):
    flips = [
        'https://i.imgur.com/OBHglwj.png',
        'https://i.imgur.com/nQeGRPz.jpg',
        'https://i.imgur.com/WS9TH5W.png',
        'https://i.imgur.com/DkdWlO4.png',
    ]
    await ctx.send(flips[random.randrange(len(flips))])