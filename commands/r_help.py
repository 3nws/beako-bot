async def commands_help(i, help_ins):
    message = help_ins.get_help()
    if message is None:
        message = 'No such command available!'
    await i.response.send_message(message)
