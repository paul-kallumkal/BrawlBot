import os
import discord
from active import active
from read_message import stat_msg, set_msg, cmd_msg, help_msg, auto_msg, reset_msg, stop_msg
from functions import role_check, automate, warn_admins
from replit import db

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('Login successful as {0.user}'.format(client))
  if len(db['guilds'].keys())== 0:
    db['guilds'] = {}
  await automate(client)

@client.event
async def on_guild_join(guild):
  if(await role_check(guild)):
    db['guilds'][str(guild.id)]=True 
  else:
    await warn_admins(guild)
  
@client.event
async def on_guild_leave(guild):
  if(str(guild.id) in db['guilds'].keys()):
    db['guilds'].pop(str(guild.id))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  await stat_msg(message)
  await set_msg(client, message)
  await cmd_msg(message)
  await help_msg(message)
  await stop_msg(client, message)

  await auto_msg(message)
  await reset_msg(client, message)

active()
client.run(os.environ['BOT_TOKEN'])