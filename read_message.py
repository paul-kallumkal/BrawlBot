from functions import get_data,set_role, role_check
from replit import db
import discord
import asyncio

async def cmd_msg(message):
  if(message.content.startswith('?commands')):
    await message.channel.send('Commands:\n?commands: Shows list of commands\n?help: Get assistance linking your account\n?rank: Get your game statistics\n?set (Your ID): Allots a server role based on your ranked tier\n?stop: Stop tracking your brawlhalla profile\n\nAdmin only\n?auto (true/false): Manage automatic role update\n?reset: Reset server roles (may take a while to update all members)')
  
async def help_msg(message):
  if(message.content.startswith('?help')):
    await message.channel.send('Help:\nUse ?commands to avail a list of commands\nSet up your ID by using ?set (your ID)\nFind your brawlhalla ID under your inventory or look it up at <https://brawldb.com/search>\n')
    await message.channel.send(file=discord.File('help.png'))

async def stat_msg(message):
  if(message.content.startswith('?stats') or message.content.startswith('?rank')):
    if(str(message.author.id) not in db.keys()):
      return await message.channel.send('First set up your ID (?set)')
    data = get_data(db[str(message.author.id)])
    if('tier' not in data):
      return await message.channel.send(data)
    await message.channel.send(f"Name: {data['name']}\nTier: {data['tier']}\nRating: {data['rating']}\tPeak Rating: {data['peak_rating']}\nGames: {data['games']}\t\tWins: {data['wins']}\nBest legend: " + max(data['legends'], key=lambda x:x['rating'])['legend_name_key'].capitalize())

async def set_msg(client, message):
  if(message.content.startswith('?set')):
    data = get_data(message.content.split()[1])
    if(data == "Unranked"):
      return await message.channel.send("Invalid ID. Try ?help")
    if(data == "Too many requests, try again later"):
      return await message.channel.send(data)
    w1 = await message.channel.send(f"Name: {data['name']}\nTier: {data['tier']}\nELO: {data['rating']}\n\nIs this correct?")
    await w1.add_reaction("❌")
    await w1.add_reaction("✅")
    def react_check(reaction, user):
      return reaction.message == w1 and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌") and user == message.author
    try: 
      reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=react_check)
      if str(reaction.emoji)=="❌":
        return await message.channel.send("Aborted")
    except asyncio.TimeoutError:
      return await message.channel.send("You did not react in time")
    await set_role(message.author,data['tier'].split()[0])
    db[str(message.author.id)] = message.content.split()[1]
    await message.channel.send("ID set up successfully!")

async def stop_msg(client, message):
  if(message.content.startswith('?stop')):
    w1 = await message.channel.send("Warning: You will have to set up your ID again if you want automatic role updates. Proceed?")
    await w1.add_reaction("❌")
    await w1.add_reaction("✅")
    def react_check(reaction, user):
      return reaction.message == w1 and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌") and user == message.author
    try: 
      reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=react_check)
      if str(reaction.emoji)=="❌":
        return await message.channel.send("Aborted")
    except asyncio.TimeoutError:
      return await message.channel.send("You did not react in time")
    del db[str(message.author.id)]
    await message.channel.send("Updates stopped")
    
#admin commands

async def auto_msg(g_list, message):
  if(message.content.startswith('?auto')):
    if(message.content == '?auto'):
      return await message.channel.send("Automatic role update is" + "on" if g_list[message.guild] else "off")
    if(message.author.guild_permissions.administrator):
      g_list[message.guild] = 'true' == message.content.split()[1].lower()
      if(g_list[message.guild]):
        return await message.channel.send("Automatic role update is on")
      return await message.channel.send("Automatic role update is off")
    await message.channel.send("Admin permissions required")

async def reset_msg(client, message):
  if(message.content == '?reset'):
    if(message.author.guild_permissions.administrator):
      w1 = await message.channel.send("Warning: This will reset all tier roles. Proceed?")
      await w1.add_reaction("❌")
      await w1.add_reaction("✅")
      def react_check(reaction, user):
        return reaction.message == w1 and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌") and user == message.author
      try: 
        reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=react_check)
        if str(reaction.emoji)=="❌":
          return await message.channel.send("Aborted")
      except asyncio.TimeoutError:
        return await message.channel.send("You did not react in time")
      w2 = await message.channel.send("Ensure the BrawlBot is positioned higher than tier related roles")
      await w2.add_reaction("❌")
      await w2.add_reaction("✅")
      def react_check2(reaction, user):
        return reaction.message == w2 and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌") and user == message.author
      try: 
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=react_check2)
        if str(reaction.emoji)=="❌":
          return await message.channel.send("Aborted")
      except asyncio.TimeoutError:
        return await message.channel.send("You did not react in time")
      await role_check(message.guild)
      return await message.channel.send("Reset complete")
    await message.channel.send("Admin permissions required")