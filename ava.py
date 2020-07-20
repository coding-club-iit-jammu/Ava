import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()

server = os.getenv("SERVER")
TOKEN = os.getenv('DISCORD_TOKEN')

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
        
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )
@bot.command()
async def leave(member):
    await member.send('Leaving server. BYE!')
    await bot.close()
    exit()    
'''
@bot.command()
async def verify(member):
    await member.send("starting")
'''
bot.run(TOKEN)