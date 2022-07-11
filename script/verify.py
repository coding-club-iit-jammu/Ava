import json
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

from oauth.google_auth_service import GoogleAuthService, UserNotVerifiedException

from .log import log_emit

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb[os.getenv("DOCUMENT")]

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

def is_2021_student(enum):
    year = enum[0:4]
    if year == "2021":
        return True
    return False

path = os.path.realpath(
  os.path.join(
    os.path.dirname(__file__), '..', 'data', '2021_selected_students.json'))

def is_2021_student_selected(email):
    with open(path) as rf:
        data = json.load(rf)

    if email.lower() in data['students']:
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

    async def give_roles(self, member, entry_number):
        print(entry_number)
        if((entry_number[4] == 'U' and int(entry_number[:4]) > 2017 ) or (entry_number[4] == 'P' and int(entry_number[:4]) >= 2020 ) or entry_number[4] == 'R'):
            roles = entry_number[:5]+"G"
        else:
            roles = "Alumni"
        print(roles)
        try:
            stu_type = discord.utils.get(guild.roles, name=roles)
            await member.add_roles(stu_type)
        except:
            perms = discord.Permissions(send_messages=False, read_messages=True)
            await guild.create_role(name=roles, permissions=perms, mentionable = True)
            stu_type = discord.utils.get(guild.roles, name=roles)
            await member.add_roles(stu_type)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def verify(self, ctx, name : str = "", entry_number : str = ""):
        name = name.strip()
        if(ctx.guild is not None):
            return await ctx.send(f'Please DM for Verification')
        if(name == "" or entry_number ==""):
            help_msg = 'Please use .verify command in correct format.\nFor eg.\n.verify "Abhishek Chaudhary" 2018ucs0087'
            return await ctx.send(f'{help_msg}')
        user_ex = db.member.find_one({'entry' : entry_number}, {'discordid':1})
        print(name, entry_number)
        if(user_ex is not None):
            if(ctx.author.id != int(user_ex['discordid'])):
                return await ctx.send("One discord Id already registered")
        await logs.print(f'{ctx.author.mention} tried to join having entry number {entry_number}')
        return await ctx.send(f'We`ve stopped entries temporarily, Contact Core team')
        timeout = 3
        entry_number = entry_number.upper()
        if(check_entry_number(entry_number) == False):
            return await ctx.send("Invalid Entry Number")
        email = entry_number + "@iitjammu.ac.in"

        if is_2021_student(entry_number) and not is_2021_student_selected(email):
            await logs.print(f'{ctx.author.mention} tried to join having entry number {entry_number} but was not allowed')
            return await ctx.send("Student with the given id was not selected in the club")

        if(await self.authorize_user(ctx, logs, name, entry_number) == True):
            await logs.print(f'{ctx.author.mention} verified')
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
            await member.add_roles(role)
            await self.give_roles(member, entry_number)
            await ctx.send(f"verified {ctx.author}")
            await logs.print(f'{ctx.author.mention} Roles given')
        else:
            await ctx.send(f"not verified {ctx.author}")
            await logs.print(f'{ctx.author.mention} verification failed')

    @commands.command()
    @commands.has_role('Admin')
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def update_roles(self, ctx):
        _role = discord.utils.get(guild.roles, name="Verified")
        all_members = _role.members
        all_users = db.member.find({}, {"entry" : 1, "discordid" : 1})
        user_dic = {}
        for user in all_users:
            user_dic[user['discordid']] = user['entry']
        for member in all_members:
            mem_id = member.id
            print(mem_id, '---')
            try:
                mem_entry = user_dic[str(mem_id)]
                print(mem_entry)
            except Exception as e:
                print(e)
                continue
            else:
                await self.give_roles(member, mem_entry)
        await ctx.send("Roles Updated")

    async def authorize_user(self, ctx, logs, name, entry_number):
        try:
            google_auth_service = GoogleAuthService()
            auth_url = google_auth_service.auth_url()
        except Exception as err:
            await logs.print(err)
            return False

        verication_message = (
            'Please visit the following link for verification and send back '
            'the authorization code provided at the end of authorization: {}'
        )

        await ctx.send(f'Name : {name}\nEntry Number : {entry_number}\n' +
            verication_message.format(auth_url[0]))

        print(ctx.author, 'Verification Started')
        await logs.print(f'{ctx.author.mention} started Verification')

        try:
            authorization_code = (await self.bot.wait_for(
                'message', check=lambda message: message.author == ctx.author,
                timeout = 180)).content
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author} Verification Time Out")
            return await logs.print(f'{ctx.author.mention} verification Timeout')

        try:
            user_email = google_auth_service.validate_and_get_user_email(
                authorization_code)
        except UserNotVerifiedException:
            await logs.print(f'{ctx.author.mention} tried to verify using non verified google account')
        except Exception as err:
            await logs.print(err)
        else:
            if entry_number.lower() + '@iitjammu.ac.in' == user_email:
                return True
            else:
                # Handle account and entry number mismatch
                await ctx.send('Your verification account doesnot match with the entry number\n' +
                                'Please, check for typing errors')
                await logs.print(f'{ctx.author.mention} tried to verify using wrong entry number : {entry_number}')
                await logs.print(f'{ctx.author.mention} provided entry number {entry_number} and used {user_email}')

        return False


def setup(bot):
    print("-----",server)
    bot.add_cog(Verify(bot))
