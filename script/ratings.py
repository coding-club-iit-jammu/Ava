import os
import time
import re
import discord
from discord.ext import commands
from pymongo import MongoClient
from .log import log_emit

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb[os.getenv("DOCUMENT")]


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
    
    async def increaseXP(self, userid, addXP, timelimit = True):
        userid = str(userid)
        user = db.member.find_one({"discordid" : userid},{"rating" : 1, "last_message" : 1, "rating" : 1})
        if(user is None):
            return
        if(timelimit == False or (time.time() - user['last_message'] >= 60) ):
            new_rating = user['rating'] + addXP
            prev_lvl = user['rating']//100 + 1
            new_lvl = new_rating//100 + 1
            if(timelimit):
                new_user = {
                    '$set' : {
                        'last_message' : time.time(),
                        'rating' : new_rating
                    }
                }
            else:
                new_user = {
                    '$set' : {
                        'rating' : new_rating
                    }
                }
            if(new_lvl > prev_lvl):
                lvl_channel = self.bot.get_channel(int(os.getenv('LEVEL_CHANNEL')))
                author = self.bot.get_user(int(userid))
                await lvl_channel.send(f"Congratulations {author.mention} for just advancing to level {new_lvl}")
            key_dat = {"discordid" : userid}
            db.member.update(key_dat, new_user)

    @commands.command()
    @commands.has_role('everyone')   
    async def changeXP(self,ctx, member, addXP:int):
        if(len(member) < 3):
            return await ctx.send(f"{ctx.author.mention} Pls enter minimum of 3 charaters")
        con = False
        if(re.search("^<@!.*>$", member)):
            userid = member[3:-1]
            con = True
        elif(re.search("^<@.*>$", member)):
            if(member[2] == '&'):
                return await ctx.send(f"{ctx.author.mention} Invalid Mention")
            userid = member[2:-1]
            con = True
        if(con == False):
            return await ctx.send(f"{ctx.author.mention} Invalid Mention")
        author = self.bot.get_user(int(userid))
        if(addXP < 0):
            stat = "decreased"
        else:
            stat = "increased"
        await ctx.send(f"{ctx.author.mention} forcefully {stat} {author.mention}`s XP by {max(addXP,addXP*-1)}")
        await self.increaseXP(userid, addXP, False)


    @commands.command()
    @commands.has_role('Verified')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rating(self, ctx,member : str = ""):
        if (isinstance(ctx.channel, discord.channel.TextChannel) == False):
            return await ctx.send("You can`t use commands other than '.verify' in private messages 🛑")
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
        em.set_footer(text=f'Requested by: {ctx.author.name}\t\tResponse Time : {round(self.bot.latency, 3)}s')
        await ctx.send(embed = em)

    @commands.command()
    @commands.has_role('Verified')
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def ranklist(self, ctx, upto : int = 5):
        if (isinstance(ctx.channel, discord.channel.TextChannel) == False):
            return await ctx.send("You can`t use commands other than '.verify' in private messages 🛑")
        core_role = discord.utils.get(guild.roles, name="Core Team")  
        user_roles = ctx.author.roles
        if(core_role not in user_roles):
            upto = 5
        users = db.member.find({},{"name" : 1, "rating" : 1, "entry" : 1})
        all_member = []
        for user in users:
            tem = (user['entry'], user['name'], user['rating'])
            all_member.append(tem)
        all_member.sort(key = lambda x : x[2], reverse=True)
        
        em = discord.Embed(title="XP Ranklist", colour = discord.Colour(16737945))
        '''
        names = ""
        entry_all = ""
        ratings = "" 
        times = 0
        for i in all_member:
            names = names +  i[1][:15] + "\n"
            #entry_all = entry_all + i[0] + "\n"
            ratings = ratings + str(i[2]) + "\n"
            times += 1
            if(times >= upto):
                break
        em.add_field(name='Name', value=names, inline=True)
        #em.add_field(name='Username', value=entry_all, inline=True)
        em.add_field(name='Ratings', value=ratings, inline=True)
        '''
        name_len = 28
        header = "Name" 
        header_final = header + (" "*(name_len - len(header))  ) + "Rating"
        values = ""
        times = 0
        for i in all_member:
            iname = i[1][:15] + f" ({i[0][:4]})"
            tem = iname + (" "*(name_len - len(iname))  ) + str(i[2])
            values = values + tem + "\n"
            times += 1
            if(times >= upto):
                break
        values = "```" + values + "```"
        em.add_field(name=header_final, value=values)
        em.set_footer(text=f'Requested by: {ctx.author.name}\t\tResponse Time : {round(self.bot.latency, 3)}s')
        await ctx.send(embed = em)
        
def setup(bot):
    print("ratings command added")   
    bot.add_cog(Ratings(bot))
