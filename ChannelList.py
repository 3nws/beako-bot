from commands.db.r_db import commands_add_channel_rz, commands_add_channel_kaguya, commands_add_channel_onk,\
                            commands_remove_channel_rz, commands_remove_channel_kaguya, commands_remove_channel_onk

class ChannelList:
    def __init__(self, series, channel_id):
        self.series = series
        self.channel_id = channel_id
        
    async def add_channel(self):
        if self.series == "rezero" or self.series == "rz":
            res = await commands_add_channel_rz(self.channel_id)
        elif self.series == "kaguya" or self.series == "kaguya-sama":
            res = await commands_add_channel_kaguya(self.channel_id)
        elif self.series == "onk" or self.series == "oshi no ko":
            res = await commands_add_channel_onk(self.channel_id)
        else:
            res = "To what list do you want to add this channel, in fact?!"
        return res
        
    async def remove_channel(self):
        if self.series == "rezero" or self.series == "rz":
            res = await commands_remove_channel_rz(self.channel_id)
        elif self.series == "kaguya" or self.series == "kaguya-sama":
            res = await commands_remove_channel_kaguya(self.channel_id)
        elif self.series == "onk" or self.series == "oshi no ko":
            res = await commands_remove_channel_onk(self.channel_id)
        else:
            res = "From what list do you want to remove this channel, in fact?!"
        return res