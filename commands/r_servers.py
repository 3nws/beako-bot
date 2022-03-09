async def commands_servers(ctx, bot):
    print(f'Logged in as: {bot.user.name}\n')
    print(f'Server List ({len(bot.guilds)})\n')
    server_counter = 1
    for guild in bot.guilds:
        print(f"{server_counter}. {guild.name}")
        server_counter += 1
