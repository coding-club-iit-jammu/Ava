import os
import time
import re
import discord
import random
from discord.ext import commands
from pymongo import MongoClient
from .log import log_emit

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb.CodingClub


server = int(os.getenv("SERVER"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
DEBUG = (os.getenv("DEBUG","") != "False" )

class Ratings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        global logs, guild
        guild = self.bot.get_guild(int(server))
        logs = log_emit(LOG_CHANNEL, self.bot, DEBUG)

    async def increaseXP(self, message):
        userid = str(message.author.id)
        user = db.member.find_one({"discordid" : userid},{"rating" : 1, "last_message" : 1, "rating" : 1})
        if(user is None):
            return
        if(time.time() - user['last_message'] >= 30):
            new_rating = user['rating'] + random.randint(5,10)
            prev_lvl = user['rating']//100 + 1
            new_lvl = new_rating//100 + 1
            new_user = {
                '$set' : {
                    'last_message' : time.time(),
                    'rating' : new_rating
                }
            }
            if(new_lvl > prev_lvl):
                await message.channel.send(f"Congratulations {message.author.mention} for just advancing to level {new_lvl}")
            key_dat = {"discordid" : userid}
            db.member.update(key_dat, new_user)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rating(self, ctx,member : str = ""):
        if(re.search("^<@!.*>$", member)):
            userid = member[3:-1]
        elif(re.search("^<@.*>$", member)):
            if(member[2] == '&'):
                return await ctx.send(f"{ctx.author.mention} Invalid Mention")
            userid = member[2:-1]
        elif(member.isnumeric()):
            userid = member
        else:
            userid = str(ctx.author.id)
            
        user = db.member.find_one({"discordid" : userid},{"name" : 1, "rating" : 1, "username" : 1})
        if(user is None):
            msg = '```' + "Invalid parameters" + "```"
            return await ctx.send(msg)
        level = user['rating']//100 + 1
        user_obj = guild.get_member(int(userid))
        stats = f"User : {user_obj.mention}\nLevel : {level}\nXP : {user['rating']}"
        
        em = discord.Embed(title="Ratings Stats", description=stats)
        em.set_thumbnail(url=user_obj.avatar_url)
        em.set_footer(text='Requested by: ' + ctx.author.name)
        await ctx.send(embed = em)
        
def setup(bot):
    print("ratings command added")   
    bot.add_cog(Ratings(bot))