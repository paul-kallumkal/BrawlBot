from functions import get_data,set_role
from replit import db
import discord

async def cmd_msg(message):
  if(message.content.startswith('?commands')):
    await message.channel.send('Commands:\n?commands: Shows list of commands\n?help: Helps you link your account\n?rank: Provides your game statistics\n?setID (Your ID): Gives you a server role based on your ranked tier\n\nAdmin only\n?autoset true/false: manage automatic role update')
  
async def help_msg(message):
  if(message.content.startswith('?help')):
    await message.channel.send('Help:\nUse ?commands to avail a list of commands\nSet up your ID by using ?setid (your ID)\nFind your brawlhalla ID under your inventory or look it up at <https://brawldb.com/search>\n')
    await message.channel.send(file=discord.File('help.png'))

async def stat_msg(message):
  if(message.content.startswith('?stats') or message.content.startswith('?rank')):
    if(str(message.author) not in db.keys()):
      return await message.channel.send('First set up your ID (?setid)')
    data = get_data(db[str(message.author)])
    if(data == "Unranked"):
      return await message.channel.send("Unranked")
    await message.channel.send(f"Name: {data['name']}\nTier: {data['tier']}\nRating: {data['rating']}\tPeak Rating: {data['peak_rating']}\nGames: {data['games']}\t\tWins: {data['wins']}\nBest legend: " + max(data['legends'], key=lambda x:x['rating'])['legend_name_key'].capitalize())

async def id_msg(message):
  if(message.content.startswith('?setid')):
    data = get_data(message.content.split()[1])
    if(data == "Unranked"):
      return await message.channel.send("Invalid ID. Try ?help")
    #add confirmation message through reaction
    await set_role(message.author,data['tier'].split()[0])
    db[str(message.author)] = message.content.split()[1]
    await message.channel.send("ID set up successfully!")

#admin commands

async def auto_msg(message):
  if(message.content.startswith('?autoset')):
    #Use and admin permissions required
    auto = 'true' == message.content.split()[1].lower()
    #change the server auto variable
    if(auto):
      return await message.channel.send("Automatic role update is on")
    return await message.channel.send("Automatic role update is off")
    #await message.channel.send("Admin permissions required")