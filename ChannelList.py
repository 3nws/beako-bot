from commands.db.r_db import commands_add_channel, commands_remove_channel


class ChannelList:
    def __init__(self, series, channel_id):
        self.series = series
        self.channel_id = channel_id

    async def add_channel(self, bot, ctx):
        res = await commands_add_channel(bot, ctx, self.channel_id, self.series)
        return res

    async def remove_channel(self):
        res = await commands_remove_channel(self.channel_id, self.series)
        return res
