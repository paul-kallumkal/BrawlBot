import os
import discord
from active import active
from read_message import rank_msg, cmd_msg, help_msg, auto_msg, reset_msg, stop_msg, ghot_msg,lite_msg, stat_msg, info_msg
from functions import role_check, automate, warn_admins
from replit import db

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('Login successful as {0.user}'.format(client))
  await client.change_presence(activity=discord.Game('against Sandstorm'))
  return await automate(client)

@client.event
async def on_guild_join(guild):
  if(await role_check(guild)):
    db['guilds'][str(guild.id)]=True 
  else:
    await warn_admins(guild)
  return 
  
@client.event
async def on_guild_leave(guild):
  if(str(guild.id) in db['guilds'].keys()):
    db['guilds'].pop(str(guild.id))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  await rank_msg(message)
  await stat_msg(message)
  await cmd_msg(message)
  await help_msg(message)
  await stop_msg(client, message)
  await ghot_msg(message)
  await lite_msg(message)
  await info_msg(message)
  #admin commands
  await auto_msg(message)
  return await reset_msg(client, message) 

active()
client.run(os.environ['BOT_TOKEN'])
