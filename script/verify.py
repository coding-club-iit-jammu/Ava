import os
from discord.ext import commands

server = os.getenv("SERVER")

class Verify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self, ctx, name : str = "", entry_number : str = ""):
        guild = self.bot.get_guild(int(server))
        if(ctx.guild is not None):
            return await ctx.send(f'Please DM for Verification')
        if(name == "" or entry_number ==""):
            help_msg = 'Please use !verify command in correct format.\nFor eg.\n!verify "Abhishek Chaudhary" 2018ucs0087'
            return await ctx.send(f'{help_msg}')
        timeout = 3
        entry_number = entry_number.upper()
        email = entry_number + "@iitjammu.ac.in"
        verf_msg = f"An email with Verification Code has been sent to {email}. Enter your code here within {timeout} minutes."
        await ctx.send(f'Name : {name}\nEntry Number : {entry_number}\n{verf_msg}')
        '''
        code_got = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if(name.content[0] == "!"):
            return
        await ctx.send(f"name got {name.content}")
        '''


def setup(bot):
    print("-----",server)
    bot.add_cog(Verify(bot))