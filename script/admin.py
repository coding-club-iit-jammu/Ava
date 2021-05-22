import os
import time
import re
import asyncio
import discord
from discord.ext import commands
from discord.utils import resolve_invite
from pymongo import MongoClient
from .log import log_emit

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb[os.getenv("DOCUMENT")]

server = int(os.getenv("SERVER"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
DEBUG = (os.getenv("DEBUG","") != "False" )

async def give_role(member, roles):
    try:
        role_obj = discord.utils.get(member.guild.roles, name=roles)
        await member.add_roles(role_obj)
    except:
        perms = discord.Permissions(send_messages=True, read_messages=True)
        await member.guild.create_role(name=roles, permissions=perms, mentionable = True)
        role_obj = discord.utils.get(member.guild.roles, name=roles)
        await member.add_roles(role_obj)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        global logs, guild
        guild = self.bot.get_guild(int(server))
        logs = log_emit(LOG_CHANNEL, self.bot, DEBUG)

    @commands.command()
    @commands.has_role('Admin')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def addStudents(self, ctx, role_name: str = ""):
        if(role_name == ""):
            return await ctx.send(f"{ctx.author.mention} Please pass role name")
        await ctx.send(f"{ctx.author.mention} Please pass Student`s Entry number in next message")
        try:
            resp_got = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 180)
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author} Time Out")
        students_list = resp_got.content.split()
        member_db = db.member.find({},{'discordid':1, 'entry':1})
        tmp_lst = []
        member_dict = {}
        for member in member_db:
            member_dict[member['entry']] = []
            tmp_lst.append(member)
        for member in tmp_lst:
            member_dict[member['entry']].append(member['discordid'])
        logs = "Students having entry number: "
        for student in students_list:
            con = False
            for single_id in member_dict.get(student.upper(),[]):
                single_member = ctx.guild.get_member(int(single_id))
                if(single_member is None):
                    continue
                await give_role(single_member, role_name)
                con = True
                print(f"given {role_name} role to ", student, 'having discord id ', single_id)
            if(con):
                logs +=  "\n" + student
        logs += f"\nAre added to {role_name}"
        await ctx.send(f"```{logs}```") 
    
    @commands.command()
    @commands.has_role('Admin')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def kickbyID(self, ctx : commands.Context, reason: str = ""):
        reason = reason.strip()
        if(reason == ''):
            return await ctx.send(f"{ctx.author.mention} Please pass reason to kick")
        await ctx.send(f"{ctx.author.mention} Please pass Student`s Entry number in next message")
        try:
            resp_got = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 180)
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author} Time Out")
        students_list = resp_got.content.strip('`').split()

        member_db = db.member.find({},{'discordid':1, 'entry':1})
        tmp_lst = []
        member_dict = {}
        for member in member_db:
            member_dict[member['entry']] = []
            tmp_lst.append(member)
        for member in tmp_lst:
            member_dict[member['entry']].append(member['discordid'])

        for student in students_list:
            for single_id in member_dict.get(student.upper(),[]):
                print(single_id,'----------')
                single_member = ctx.guild.get_member(int(single_id))
                print(single_member)
                if(single_member is None):
                    continue
                await single_member.kick(reason = reason)
                print("kicked", single_member)
                await logs.print(f"Kicked {single_member.mention} as requested by {ctx.author.mention}")
        return await ctx.send(f"```Kicked all members requested```")  
        

def setup(bot):
    print("admin command added")   
    bot.add_cog(Admin(bot))
