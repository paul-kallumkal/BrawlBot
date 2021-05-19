from functions import get_ranked, role_check, get_data, set_role,unset_role, calc_glory
from data import get_legends
from replit import db
import asyncio

async def info_msg(message):
  if(message.content.lower().startswith('bb info')):
    if(len(message.content.split()) < 3):
      return await message.channel.send('Incorrect format (example: bb info Ulgrim)')
    name = message.content[8:].lower()
    legends = get_legends()
    for legend in legends:
      if legend['legend_name_key']==name:
        return await message.channel.send(f"Name: {legend['bio_name']}\nBot Name: {legend['bot_name']}\nTitle: {legend['bio_aka']}\n\n{legend['bio_text']}\n\nWeapons: {legend['weapon_one']}, {legend['weapon_two']}\nStrength: {legend['strength']}\tDexiterity: {legend['dexterity']}\nDefense: {legend['defense']}\t Speed: {legend['speed']}")
    return await message.channel.send("Legend can't be found, please check your spelling and try again")

async def cmd_msg(message):
  if(message.content.lower() == 'bb commands' or message.content.lower() == 'bb command'):
    await message.channel.send("Commands:\nbb commands: Shows list of commands\nbb help: Get assistance linking your account\nbb profile: Get your game statistics\nbb ranked: get your ranked statistics\nbb info (name): Get a legend's backstory and stats\nbb add: Link your steam to get a server role based on your ranked tier\nbb stop: Stop tracking your brawlhalla profile\n\nAdmin only\nbb auto (true/false): Manage automatic role update\nbb reset: Reset server roles (may take a while to update all members)")
  
async def help_msg(message):
  if(message.content.lower() == 'bb help'):
    await message.channel.send("Help:\nUse bb commands to avail a list of commands\nUnder Discord Settings->Connections link your Steam profile to Discord\nThen head to <http://brawlbot.ml> to activate your BrawlBot profile instantly")

async def rank_msg(message):
  if(message.content.lower() == 'bb ranked' or message.content.lower() == 'bb rank'):
    if(str(message.author.id) not in db.keys()):
      return await message.channel.send('First set up your ID (bb add)')
    data = get_ranked(db[str(message.author.id)])
    if('tier' not in data):
      return await message.channel.send(data)
    await set_role(message.author,data['tier'].split()[0])
    return await message.channel.send(f"Name: {data['name'].encode('latin').decode()}\nTier: {data['tier']}\nRating: {data['rating']}\tPeak Rating: {data['peak_rating']}\nGames: {data['games']}\t\tWins: {data['wins']}\nBest legend: {max(data['legends'], key=lambda x:x['rating'])['legend_name_key'].capitalize()}\nExpected glory: {calc_glory(int(data['wins']),int(data['peak_rating']))}")

async def stat_msg(message):
  if(message.content.lower() == 'bb stats' or message.content.lower() == 'bb profile'):
    if(str(message.author.id) not in db.keys()):
      return await message.channel.send('First set up your ID (bb add)')
    data = get_data(db[str(message.author.id)])
    if('name' not in data):
      return await message.channel.send(data)
    await message.channel.send(f"Name: {data['name'].encode('latin').decode()}\nLevel: {data['level']}\nGames: {data['games']}\tWins: {data['wins']}\nBest legend: " + max(data['legends'], key=lambda x:x['level'])['legend_name_key'].capitalize())

async def allstat_msg(message):
   if(message.content.lower() == 'bb stats' or message.content.lower() == 'bb profile'):
    if(str(message.author.id) not in db.keys()):
      return await message.channel.send('First set up your ID (bb add)')
    data = get_data(db[str(message.author.id)])
    if('name' not in data):
      return await message.channel.send(data)
    clan = ""
    if("clan" in data):
      clan = "\nClan: " + data['clan']['clan_name']

    await message.channel.send(f"Name: {data['name'].encode('latin').decode()}\nLevel: {data['level']}\nGames: {data['games']}\tWins: {data['wins']}\nBest legend: " + max(data['legends'], key=lambda x:x['level'])['legend_name_key'].capitalize() + clan)

async def add_msg(client, message):
  if(message.content.lower() == 'bb add' or message.content.lower() == 'bb set'):
    return await message.channel.send("If you've linked your Steam to Discord, head to <http://brawlbot.ml> to set up your BrawlBot profile instantly")

async def stop_msg(client, message):
  if(message.content.lower() == 'bb stop'):
    if str(message.author.id) not in db.keys():
      await unset_role(message.author)
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
    await unset_role(message.author)
    await message.channel.send("Updates stopped")

async def ghot_msg(message):
  if(message.content.lower() == 'bb ghot'):
    await message.channel.send("Don't do this to yourself. Studies lite, Brawlhalla all night!")

async def lite_msg(message):
  if(message.content.lower() == 'bb lite'):
    await message.channel.send("💡")
    
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
        return await message.channel.send("Unknown error encountered")
    await message.channel.send("Admin permissions required")