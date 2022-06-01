from Help import Help
from discord import Interaction

async def commands_help(i: Interaction, help_ins: Help) -> None:
    await help_ins.get_help(i)