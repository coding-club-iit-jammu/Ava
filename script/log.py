import discord
class log_emit:
    def __init__(self, log_channel, bot, DEBUG):
        self.bot = bot
        self.DEBUG = DEBUG
        if(type(log_channel) == int):
            self.logchannel = bot.get_channel(log_channel)
        else:
            guild = bot.get_guild(log_channel[0])
            self.logchannel = discord.utils.get(guild.channels, name = log_channel[1])

    async def print(self, log):
        if(self.DEBUG):
            return print(log)
        return await self.logchannel.send(log)