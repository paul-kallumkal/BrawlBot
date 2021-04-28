import os
import discord
import asyncio
from active import active
from read_message import stat_msg, set_msg, cmd_msg, help_msg, auto_msg, reset_msg, stop_msg
from functions import role_check, automate, warn_admins
from replit import db

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('Login successful as {0.user}'.format(client))
  db['guilds'] = []
  db['guilds'].append(client.guilds[0].id)
  print(db['guilds'][0])
  #asyncio.run(await automate(client))

@client.event
async def on_guild_join(guild):
  if(await role_check(guild)):
    db['guilds'].append(guild.id) 
  else:
    warn_admins(guild)
  
@client.event
async def on_guild_leave(guild):
  del db[guild.id]

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  await stat_msg(message)
  await set_msg(client, message)
  await cmd_msg(message)
  await help_msg(message)
  await stop_msg(message)

  await auto_msg(message)
  await reset_msg(client, message)

active()
client.run(os.environ['BOT_TOKEN'])