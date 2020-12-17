import discord
import os
import sendgrid
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from pymongo import MongoClient
from .log import log_emit
from discord_markdown.discord_markdown import convert_to_html

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
        correct_one = '✅'
        correct_all = '↗️'
        wrong = '❌'
        out = f'{correct_one} : Only to Members subscribed to Receive Emails\n{correct_all} : All members in the Channel (Try to avoid)\n{wrong} : To cancel'
        em = discord.Embed(title="Send Email", description=f'Are you sure to send mail to members in this channel')
        em.add_field(name="\u200b", value=f'{correct_one}\nOnly to Members subscribed to Receive Emails')
        em.add_field(name="\u200b", value=f'{correct_all}\nAll members in the Channel (Try to avoid)')
        em.add_field(name="\u200b", value=f'{wrong}\nCancel the process')
        em.set_thumbnail(url=message.author.avatar_url)
        em.set_footer(text='Requested by: ' + message.author.name)
        msg = await message.channel.send(embed=em)
        await msg.add_reaction(correct_one)
        await msg.add_reaction(correct_all)
        await msg.add_reaction(wrong)
        try:
            rec_got, rec_user = await self.bot.wait_for('reaction_add', check=lambda rec_msg,rec_auth: rec_auth == message.author, timeout = 180)
        except asyncio.TimeoutError:
            await msg.delete()
        else:
            if(rec_got.emoji in [correct_one, correct_all]):
                con_email = False
                if(rec_got.emoji == correct_all):
                    con_email = True
                all_users = self.db.member.find({}, {"name" : 1, "entry" : 1, "discordid" : 1})
                user_dict = {}
                for user in all_users:
                    user_dict[user['discordid']] = user['entry']
                channel_members = message.channel.members
                email_list = []
                email_role = discord.utils.get(self.guild.roles, name="Receive Emails")
                alum_role = discord.utils.get(self.guild.roles, name="Alumni") 
                for eachmember in channel_members:
                    if((con_email or email_role in eachmember.roles) and (alum_role not in eachmember.roles)):
                        try:
                            person_id = user_dict[str(eachmember.id)] + "@iitjammu.ac.in"
                        except:
                            continue
                        email_list.append(person_id)     
                email_Subject = message.channel.name
                msg_link = f'https://discordapp.com/channels/{self.guild.id}/{message.channel.id}/{message.id}'
                emb = discord.Embed(title="Email Sent", description = 'Above message emailed to all members in following channel successfully')
                emb.set_footer(text='Email requested by: ' + message.author.name)
                msg_cont = convert_to_html(message.content)
                email_message = Mail(
                    from_email=f"Ava-noreply@{os.getenv('EMAIL_DOMAIN')}",
                    to_emails=email_list,
                    subject=email_Subject,
                    html_content= f'{msg_cont} <br>-{message.author.name} <br><br>Link to message : {msg_link}  <br>Sincerely,<br>Ava, BOT Coding Club'
                    )
                email_message.personalizations[0].add_cc(Email("codingclub@iitjammu.ac.in"))
                if(self.DEBUG == False):
                    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
                    response = sg.client.mail.send.post(request_body=email_message.get())
                    print(response.status_code)
                else:
                    print(email_message)
                await message.channel.send(embed = emb)
                await logs.print(f'{message.author.mention} sent mail from #{message.channel.name} to {len(email_list) + 1} members')
            await msg.delete()