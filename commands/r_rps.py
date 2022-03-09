import random


async def commands_rps(ctx, choice):
    if (choice == 'rock'):
        counter = 'paper'
    elif (choice == 'paper'):
        counter = 'scissors'
    else:
        counter = 'rock'

    random_pick = random.randint(1, 3)

    if (random_pick == 1):
        await ctx.send(f"HAHA! I win, I suppose! You stood no chance against my {counter}, in fact!")
    elif (random_pick == 2):
        await ctx.send(f"Well that's a draw, I suppose!")
    else:
        await ctx.send(f"Betty lost, I suppose! I knew I should have picked {counter}, in fact!")
