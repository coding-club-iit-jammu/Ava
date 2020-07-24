import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from script.log import log_emit
load_dotenv()

server = os.getenv("SERVER")
TOKEN = os.getenv('DISCORD_TOKEN')
DEPARTMENT_MESSAGE = int(os.getenv("DEPARTMENT_MESSAGE"))
DEPARTMENT_CHANNEL = int(os.getenv("DEPARTMENT_CHANNEL"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))
DEBUG = (os.getenv("DEBUG","") != "False" )
AUTHOR = 664161180121825301

DEPARTMENTS = [
    ('🤖', 'Competitive Coding'),
    ('🦸', 'Development'),
    ('👨‍💻', 'AI'),
    ('🕵️', 'Security')
]

#client = discord.Client()
bot = commands.Bot(
        command_prefix='!',
        description='Coding Club IIT Jammu Discord BOT',
        case_insensitive=True    
    )

bot.load_extension('script.verify')
bot.load_extension('script.info')

@bot.event
async def on_ready():
    global logs, dep_channel, guild
    dep_channel = bot.get_channel(DEPARTMENT_CHANNEL)
    logs = log_emit(LOG_CHANNEL, bot, DEBUG)
    guild = bot.get_guild(int(server))

    role = discord.utils.get(guild.roles, name = 'Verified')
    await dep_channel.set_permissions(role, read_messages=True )
    await logs.print(f'{bot.user.mention} has connected to Discord!')
    print("connected")

        
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to Coding Club IIT Jammu Discord server. Pls Verify using !verify command followed by Name in quotes and entry number'
    )
    await logs.print(f'{member.mention} joined Server!')

@bot.command()
async def leave(ctx):
    if(ctx.message.author.id != AUTHOR):
        return
    role = discord.utils.get(guild.roles, name = 'Verified')
    await dep_channel.set_permissions(role, read_messages=False )
    await ctx.send('Leaving server. BYE!')
    await logs.print(f'{bot.user.mention} leaving Server! command from {ctx.author}.')
    await bot.close()

@bot.command()
async def ch(ctx):
    await ctx.send(f"{ctx.author.id}")

@bot.event
async def on_raw_reaction_add(payload):
    if(payload.message_id != DEPARTMENT_MESSAGE):
        return
    emoji = payload.emoji.name
    member = payload.member
    for i in DEPARTMENTS:
        if(i[0] == emoji):
            role = discord.utils.get(guild.roles, name=i[1])
            if(role in member.roles):
                return print(f"{payload.member} already assigned {role}")
            await member.add_roles(role)
            return await logs.print(f"added {payload.member.mention} to {role}")
    print("other emoji")
'''
@bot.command()
async def startup(ctx):
    start_txt = 'Join the channels by reacting with emoji of respective department'
    for i in DEPARTMENTS:
        start_txt = start_txt + "\n" + i[0] + " " + i[1]
    msg = await ctx.send(start_txt)
    guild = bot.get_guild(int(server))
    for i in DEPARTMENTS:
        emoji = i[0]
        await msg.add_reaction(emoji)
'''
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command is ratelimited, please try again in {:.2f}s'.format(error.retry_after)
        await ctx.send(msg)
    if isinstance(error, CommandNotFound):
        user_m = '{0.author.mention} '.format(ctx)
        msg_s = "Invalid Command"
        msg_s = user_m + msg_s
        await ctx.send(msg_s)
    else:
        raise error
bot.run(TOKEN)