from functions import get_data,set_role, role_check
from replit import db
import discord
import asyncio

async def cmd_msg(message):
  if(message.content == '?commands'):
    await message.channel.send('Commands:\n?commands: Shows list of commands\n?help: Get assistance linking your account\n?profile: Get your game statistics\n?id (Your ID): Allots a server role based on your ranked tier\n?stop: Stop tracking your brawlhalla profile\n\nAdmin only\n?auto (true/false): Manage automatic role update\n?reset: Reset server roles (may take a while to update all members)')
  
async def help_msg(message):
  if(message.content == '?help'):
    await message.channel.send('Help:\nUse ?commands to avail a list of commands\nSet up your ID by using ?set (your ID)\nFind your brawlhalla ID under your inventory or look it up at <https://brawldb.com/search>\n')
    await message.channel.send(file=discord.File('help.png'))

async def stat_msg(message):
  if(message.content == '?stats' or message.content == '?rank' or message.content == '?profile'):
    if(str(message.author.id) not in db.keys()):
      return await message.channel.send('First set up your ID (?set)')
    data = get_data(db[str(message.author.id)])
    if('tier' not in data):
      return await message.channel.send(data)
    await message.channel.send(f"Name: {data['name']}\nTier: {data['tier']}\nRating: {data['rating']}\tPeak Rating: {data['peak_rating']}\nGames: {data['games']}\t\tWins: {data['wins']}\nBest legend: " + max(data['legends'], key=lambda x:x['rating'])['legend_name_key'].capitalize())

async def set_msg(client, message):
  if(message.content.startswith('?id')):
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
  if(message.content == '?stop'):
    if str(message.author.id) not in db.keys():
      return await message.channel.send("Your profile is not being tracked")
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

async def auto_msg(message):
  if(message.content.startswith('?auto')):
    if(message.content == '?auto'):
      return await message.channel.send("Automatic role update is on" if str(message.guild.id) in db['guilds'].keys() else "Automatic role update is off")
    if(message.author.guild_permissions.administrator):
      if 'true' == message.content.split()[1].lower():
        db['guilds'][str(message.guild.id)]=True
        return await message.channel.send("Automatic role update is on")
      if 'false' == message.content.split()[1].lower():
        if str(message.guild.id) in db['guilds'].keys():
          db['guilds'].pop(str(message.guild.id))
        return await message.channel.send("Automatic role update is off")
      return await message.channel.send("Enter true or false after ?auto")
    await message.channel.send("Admin permissions required")

async def reset_msg(client, message):
  if(message.content == '?reset'):
    if(message.author.guild_permissions.administrator):
      w1 = await message.channel.send("Warning: This will reset all tier roles and it may take time to update all members again. Proceed?")
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
      w2 = await message.channel.send("Ensure the BrawlBot is positioned higher than tier related roles. Proceed?")
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
      if await role_check(message.guild):
        db['guilds'][str(message.guild.id)]=True
        return await message.channel.send("Reset complete")
      else:
        return await message.channel.send("Error encountered")
    await message.channel.send("Admin permissions required")