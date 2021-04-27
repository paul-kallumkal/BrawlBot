import os
import discord
from active import active
from read_message import stat_msg, id_msg, cmd_msg, help_msg, auto_msg
from functions import roll_check

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print('Login successful as {0.user}'.format(client))
  await roll_check(client)

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  await stat_msg(message)
  await id_msg(message)
  await cmd_msg(message)
  await help_msg(message)
  await auto_msg(message)

active()
client.run(os.environ['BOT_TOKEN'])