import os
import time
import re
import discord
from discord.ext import commands

from pymongo import MongoClient

from .log import log_emit

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb.CodingClub


server = int(os.getenv("SERVER"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
DEBUG = (os.getenv("DEBUG","") != "False" )

def match(a, b):
    l = min(len(a), len(b))
    a1 = a[:l].lower()
    b1 = b[:l].lower()
    if(a1 == b1):
        return True
    return False

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        global logs, guild
        guild = self.bot.get_guild(int(server))
        logs = log_emit(LOG_CHANNEL, self.bot, DEBUG)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def info(self, ctx,member : str, ver_type=""):
        if(len(member) < 3):
            return await ctx.send(f"{ctx.author.mention} Pls enter minimum of 3 charaters")
        con = False
        if(re.search("^<@!.*>$", member)):
            userid = member[3:-1]
            con = True
        elif(member.isnumeric()):
            userid = member
            con = True
        if(con):
            users = db.member.find({"discordid" : userid})
            users_len = 0
            out = ""
            for user in users:
                users_len += 1
                out = out + f"Name : {user['name']}\nEntry Number : {user['entry']}\nDiscord Id : {user['discordid']}\n\n"
            if(out == ""):
                out = "\tSorry no Member found"
            out = "```" + out + "```"
            await ctx.send(out)
            if(users_len == 1):
                dev_role = discord.utils.get(guild.roles, name="Core Team") 
                await logs.print(f"{dev_role.mention} Error occured in searching userid {userid}. If you seeing this plz report this to ADMIN ASAP.")  
        elif(ver_type.lower() == "name"):
            all_users = db.member.find()
            users = []
            for user in all_users:
                if(match(member, user['name'])):
                    users.append(user)
            out = ""
            for user in users:
                out = out + f"Name : {user['name']}\nEntry Number : {user['entry']}\nDiscord Id : {user['discordid']}\n\n"
            if(len(users) == 0):
                out = "\tSorry no Member found"
            else:
                out = f"Found total {len(users)}\n\n" + out
            out = "```" + out + "```"
            await ctx.send(out) 
        elif(ver_type.lower() == "user"):
            all_users = db.member.find()
            users = []
            for user in all_users:
                if(match(member, user['username'])):
                    users.append(user)
            out = ""
            for user in users:
                out = out + f"Name : {user['name']}\nEntry Number : {user['entry']}\nDiscord Id : {user['discordid']}\n\n"
            if(len(users) == 0):
                out = "\tSorry no Member found"
            else:
                out = f"Found total {len(users)}\n\n" + out
            out = "```" + out + "```"
            await ctx.send(out) 
        else:
            await ctx.send(f"{ctx.author.mention} Pls mention the user or his discord id as a parameter or correct ver_type, user for username and name for name")
def setup(bot):
    print("info command added")   
    bot.add_cog(Info(bot))