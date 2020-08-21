import os
import time
import discord
from discord.ext import commands
from random import randint
import string
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from pymongo import MongoClient

from .log import log_emit

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb[os.getenv("DOCUMENT")]
apidb = mongodb["API"] 

server = int(os.getenv("SERVER"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
DEBUG = (os.getenv("DEBUG","") != "False" )

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def check_entry_number(enum):
    year = enum[0:4]
    branch = enum[4:7]
    en = enum[7:]
    if(year.isdigit() and branch.isalpha() and en.isdigit()):
        return True
    return False

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_ready(self):
        global logs, guild
        guild = self.bot.get_guild(int(server))
        logs = log_emit(LOG_CHANNEL, self.bot, DEBUG)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def verify(self, ctx, name : str = "", entry_number : str = ""):
        
        if(ctx.guild is not None):
            return await ctx.send(f'Please DM for Verification')
        if(name == "" or entry_number ==""):
            help_msg = 'Please use .verify command in correct format.\nFor eg.\n.verify "Abhishek Chaudhary" 2018ucs0087'
            return await ctx.send(f'{help_msg}')
        timeout = 3
        entry_number = entry_number.upper()
        if(check_entry_number(entry_number) == False):
            return await ctx.send("Invalid Entry Number")
        email = entry_number + "@iitjammu.ac.in"
        verf_msg = f"An email with Verification Code has been sent to {email}. Enter your code here within {timeout} minutes."
        code = random_with_N_digits(6)
        
        print(ctx.author, "verification Started")
        await logs.print(f'{ctx.author.mention} started Verification')

        message = Mail(
            from_email='Ava-noreply@'+os.getenv('EMAIL_DOMAIN'),
            to_emails=email,
            subject='Coding Club Discord Server',
            html_content= f'Thanks {entry_number} for creating account on Coding Club Discord Server,<br>Your Verification Code is : <b>{code}</b><br>This Code will Expire in 3 Minutes.<br><br>Sincerely,<br>Ava, BOT Coding Club'
            )
        try:
            if(DEBUG == False):
                sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
            else:
                print(message)
        except Exception as e:
            print(e.message)
        await ctx.send(f'Name : {name}\nEntry Number : {entry_number}\n{verf_msg}')
        try:
            code_got = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 180)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author} Verification Time Out")
            return await logs.print(f'{ctx.author.mention} verification Timeout')
        if(code_got.content[0] == "."):
            return
        if(code_got.content == str(code)):
            role = discord.utils.get(guild.roles, name="Verified")
            member = guild.get_member(ctx.author.id)
            user = {
                '$set' : {
                    'name' : name,
                    'entry' : entry_number,
                    'discordid' : str(ctx.author.id),
                    'username' : ctx.author.name +'#'+ctx.author.discriminator,
                    'last_message' : time.time()
                },
                '$setOnInsert' : {
                    'rating' : 10,
                    'timestamp' : time.time(),
                }
            }

            key_dat = {'discordid' : str(ctx.author.id)}
            exist = db.member.update(key_dat, user, upsert=True)
            user = {
                '$set' : {
                    'name' : name,
                    'entry' : entry_number,
                    'discord-id' : str(ctx.author.id),
                    'username' : ctx.author.name +'#'+ctx.author.discriminator
                }
            }
            key_dat = {'entry' : entry_number}
            exist = apidb.current.update(key_dat, user, upsert=True)
            await member.add_roles(role)
            await ctx.send(f"verified {ctx.author}")
            await logs.print(f'{ctx.author.mention} verified')
        else:
            await ctx.send(f"not verified {ctx.author}")
            await logs.print(f'{ctx.author.mention} verification failed')


def setup(bot):
    print("-----",server)   
    bot.add_cog(Verify(bot))