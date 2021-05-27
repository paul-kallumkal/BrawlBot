from functions import get_ranked, role_check, get_profile, set_role, get_commands, get_help, get_setup
from data import get_info
from replit import db
import asyncio

async def info_msg(message):
  if(message.content.lower().startswith('bb info')):
    if(len(message.content.split()) < 3):
      return await message.channel.send('Incorrect format (example: bb info Ulgrim)')
    name = message.content[8:].lower()
    return await message.channel.send(get_info(name))

async def cmd_msg(message):
  if(message.content.lower() == 'bb commands' or message.content.lower() == 'bb command'):
    await message.channel.send(get_commands())
  
async def help_msg(message):
  if(message.content.lower() == 'bb help'):
    await message.channel.send(get_help())

async def rank_msg(message):
  if message.content.lower().startswith('bb rank'):
    if len(message.content.split())==2:
      member=message.author
      if(str(member.id) not in db.keys()):
        return await message.channel.send(get_setup())
    else:
      member = message.guild.get_member(int(message.content.split()[2][3:21]))
    return await message.channel.send(await get_ranked(member))

async def stat_msg(message):
  if(message.content.lower() == 'bb stats' or message.content.lower() == 'bb profile'):
    if(str(message.author.id) in db.keys()):
      return await message.channel.send(get_profile(db[str(message.author.id)]))
    return await message.channel.send(get_setup())

async def ghot_msg(message):
  if(message.content.lower() == 'bb ghot'):
    await message.channel.send("Don't do this to yourself. Studies lite, Brawlhalla all night!")

async def lite_msg(message):
  if(message.content.lower() == 'bb lite'):
    await message.channel.send("💡")

async def allstat_msg(message):
  #next update with embeds enabled
  if(message.content.lower() == 'bb allstats' or message.content.lower() == 'bb allprofile'):
    if(str(message.author.id) in db.keys()):
      data = get_profile(db[str(message.author.id)])
      if('error' in data):
        return await message.channel.send(data['error']['message'])
      clan = ""
      if("clan" in data):
        clan = "\nClan: " + data['clan']['clan_name']
      await message.channel.send(f"Name: {data['name'].encode('latin').decode()}\nLevel: {data['level']}\nGames: {data['games']}\tWins: {data['wins']}\nBest legend: " + max(data['legends'], key=lambda x:x['level'])['legend_name_key'].capitalize() + clan)
    return await message.channel.send(get_setup())

async def stop_msg(client, message):
  if(message.content.lower() == 'bb stop'):
    if str(message.author.id) not in db.keys():
      await set_role(message.author,'')
      return await message.channel.send("Your profile is not being tracked")
    w1 = await message.channel.send("Warning: You will lose any Brawlhalla associated role and will have to set up your ID again to get it back. Proceed?")
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
    await set_role(message.author,'')
    await message.channel.send("Updates stopped")

 
#admin commands

async def auto_msg(message):
  if(message.content.lower().startswith('bb auto')):
    if(message.content.lower() == 'bb auto'):
      return await message.channel.send("Automatic role update is on" if str(message.guild.id) in db['guilds'].keys() else "Automatic role update is off")
    if(message.author.guild_permissions.administrator):
      if 'true' == message.content.split()[2].lower():
        db['guilds'][str(message.guild.id)]=True
        return await message.channel.send("Automatic role update is on")
      if 'false' == message.content.split()[2].lower():
        if str(message.guild.id) in db['guilds'].keys():
          db['guilds'].pop(str(message.guild.id))
        return await message.channel.send("Automatic role update is off")
      return await message.channel.send("Enter either true or false after ?auto")
    await message.channel.send("Admin permissions required")

async def reset_msg(client, message):
  if(message.content.lower() == 'bb reset'):
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
        return await message.channel.send("An error encountered")
    return await message.channel.send("Admin permissions required")

