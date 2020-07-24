import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CommandNotFound
load_dotenv()

server = os.getenv("SERVER")
TOKEN = os.getenv('DISCORD_TOKEN')
DEPARTMENT_MESSAGE = 735924857627213904
DEPARTMENT_CHANNEL = 735879581541597204

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

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    dep_channel = bot.get_channel(735879581541597204)
    guild = bot.get_guild(int(server))
    role = discord.utils.get(guild.roles, name = 'Verified')
    await dep_channel.set_permissions(role, read_messages=True )
    print(f'{bot.user} ready to use...')

        
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to Coding Club IIT Jammu Discord server. Pls Verify using !verify command followed by Name in quotes and entry number'
    )
@bot.command()
async def leave(member):
    dep_channel = bot.get_channel(735879581541597204)
    guild = bot.get_guild(int(server))
    role = discord.utils.get(guild.roles, name = 'Verified')
    await dep_channel.set_permissions(role, read_messages=False )
    await member.send('Leaving server. BYE!')
    await bot.close()

@bot.event
async def on_raw_reaction_add(payload):
    if(payload.message_id != DEPARTMENT_MESSAGE):
        return
    guild = bot.get_guild(int(server))
    emoji = payload.emoji.name
    member = payload.member
    for i in DEPARTMENTS:
        if(i[0] == emoji):
            role = discord.utils.get(guild.roles, name=i[1])
            await member.add_roles(role)
            return print(f"added {payload.member} to {role}")
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