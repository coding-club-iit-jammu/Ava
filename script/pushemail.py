import discord
import os
import sendgrid
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from pymongo import MongoClient
from .log import log_emit

class sendemails:
    def __init__(self, bot, DEBUG):
        self.bot = bot
        self.DEBUG = DEBUG
        self.guild = bot.get_guild(int(os.getenv('SERVER')))
        global logs
        LOG_CHANNEL = int(os.getenv('LOG_CHANNEL'))
        logs = log_emit(LOG_CHANNEL,self.bot, DEBUG)

        uri = os.getenv('MONGODB')
        mongodb = MongoClient(uri)
        self.db = mongodb[os.getenv("DOCUMENT")]

    async def send(self, message):
        em = discord.Embed(title="Send Email", description='Are you sure to send mail to everyone in this channel')
        em.set_thumbnail(url=message.author.avatar_url)
        em.set_footer(text='Requested by: ' + message.author.name)
        msg = await message.channel.send(embed=em)
        correct = '✅'
        wrong = '❌'
        await msg.add_reaction(correct)
        await msg.add_reaction(wrong)
        try:
            rec_got, rec_user = await self.bot.wait_for('reaction_add', check=lambda rec_msg,rec_auth: rec_auth == message.author, timeout = 180)
        except asyncio.TimeoutError:
            await msg.delete()
        else:
            if(rec_got.emoji == correct):
                all_users = self.db.member.find({}, {"name" : 1, "entry" : 1, "discordid" : 1})
                user_dict = {}
                for user in all_users:
                    user_dict[user['discordid']] = user['entry']
                channel_members = message.channel.members
                email_list = []
                email_role = discord.utils.get(self.guild.roles, name="Receive Emails") 
                for eachmember in channel_members:
                    if(email_role in eachmember.roles):
                        try:
                            person_id = user_dict[str(eachmember.id)] + "@iitjammu.ac.in"
                        except:
                            continue
                        email_list.append(person_id)
                        
                email_Subject = message.channel.name
                emb = discord.Embed(title="Email Sent", description = 'Above message emailed to all members in following channel successfully')
                emb.set_footer(text='Email requested by: ' + message.author.name)
                email_message = Mail(
                    from_email=f"Ava-noreply@{os.getenv('EMAIL_DOMAIN')}",
                    to_emails=email_list,
                    subject=email_Subject,
                    html_content= f'{message.content}<br>-{message.author.name}<br><br>Sincerely,<br>Ava, BOT Coding Club'
                    )
                email_message.personalizations[0].add_cc(Email("abhishekchaudhary0220@gmail.com"))
                if(self.DEBUG == False):
                    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
                    response = sg.client.mail.send.post(request_body=email_message.get())
                    print(response.status_code)
                else:
                    print(email_message)
                await message.channel.send(embed = emb)
                await logs.print(f'{message.author.mention} sent mail from #{message.channel.name} to {len(email_list) + 1} members')
            await msg.delete()