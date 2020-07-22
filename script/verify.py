import os
import time
import discord
from discord.ext import commands
from random import randint

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from pymongo import MongoClient
uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb.CodingClub

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

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
        code = random_with_N_digits(6)
        print(ctx.author, "verification Started")
        message = Mail(
            from_email='Ava-noreply@iamabhishek.co.in',
            to_emails=email,
            subject='Coding Club Discord Server',
            html_content= f'Thanks {entry_number} for creating account on Coding Club Discord Server,<br>Your Verification Code is : <b>{code}</b><br>This Code will Expire in 3 Minutes.<br><br>Sincerely,<br>Ava, BOT Coding Club'
            )
        try:
            sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
        except Exception as e:
            print(e.message)
        await ctx.send(f'Name : {name}\nEntry Number : {entry_number}\n{verf_msg}')
        code_got = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 180)
        if(code_got.content[0] == "!"):
            return
        if(code_got.content == str(code)):
            role = discord.utils.get(guild.roles, name="Verified")
            member = guild.get_member(ctx.author.id)
            user = {
                'name' : name,
                'entry' : entry_number,
                'discordid' : ctx.author.id,
                'username' : ctx.author.name +'#'+ctx.author.discriminator,
                'timestamp' : time.time()
            }
            key_dat = {'discordid' : ctx.author.id}
            exist = db.member.update(key_dat, user, upsert=True)
            await member.add_roles(role)
            await ctx.send(f"verified {ctx.author}")
        else:
            await ctx.send(f"not verified {ctx.author}")


def setup(bot):
    print("-----",server)
    bot.add_cog(Verify(bot))