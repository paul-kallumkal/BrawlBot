import json
import os
import math
import requests
import asyncio
from replit import db

def get_commands():
  return "Commands:\nbb commands: Shows list of commands\nbb help: Get assistance linking your account\nbb profile: Get your game statistics\nbb ranked: get your ranked statistics\nbb info (name): Get a legend's backstory and stats\nbb stop: Stop tracking your brawlhalla profile\n\nAdmin only\nbb auto (true/false): Manage automatic role update\nbb reset: Reset server roles (may take a while to update all members)"

def get_help():
  return "Help:\nUse bb commands to avail a list of commands\nUnder Discord Settings->Connections link your Steam profile to Discord\nThen head to <http://brawlbot.ml> to activate your BrawlBot profile instantly"

def get_setup():
  return "You need to set up your ID\n1. Link your Steam to Discord under Settings->Connections\n2. Head to <http://brawlbot.ml> to set up your profile instantly"

def get_profile(brawlID):
  data = json.loads(requests.get('https://api.brawlhalla.com/player/' + str(brawlID) + '/stats?api_key=' + os.environ['API_KEY']).text)
  if 'name' in data:
    return f"Name: {data['name'].encode('latin').decode()}\nLevel: {data['level']}\nGames: {data['games']}\tWins: {data['wins']}\nBest legend: {max(data['legends'], key=lambda x:x['level'])['legend_name_key'].capitalize()}"
  if 'error' in data: 
    return data['error']['message']
  return "Failed to retrieve your profile"

async def get_ranked(member):
  if not member:
    return 'Unranked'
  data = json.loads(requests.get('https://api.brawlhalla.com/player/' + str(db[str(member.id)]) + '/ranked?api_key=' + os.environ['API_KEY']).text)
  if('error' in data):
    return data['error']['message']
  if 'tier' in data:
    await set_role(member,data['tier'].split()[0])
    return f"Name: {data['name'].encode('latin').decode()}\nTier: {data['tier']}\nRating: {data['rating']}\tPeak Rating: {data['peak_rating']}\nGames: {data['games']}\t\tWins: {data['wins']}\nBest legend: {max(data['legends'], key=lambda x:x['rating'])['legend_name_key'].capitalize()}\nExpected glory: {calc_glory(data)}"
  return 'Unranked'

def get_rank(BrawlID):
  return json.loads(requests.get('https://api.brawlhalla.com/player/' + str(BrawlID) + '/ranked?api_key=' + os.environ['API_KEY']).text)

async def set_role(member,rank):
  arr = ['Diamond','Platinum','Gold','Silver','Bronze','Tin']

  for role in member.guild.roles:
    if(role.name == rank):
      await member.add_roles(role)
    elif(role.name in member.roles and role.name in arr):
      await member.remove_roles(role)

async def role_check(guild):
  roles = ['Diamond','Platinum','Gold','Silver','Bronze','Tin']
  colours = [0xa842ff,0x55ccff,0xffdf00,0xdadada,0xee7a0b,0xa9d3e0]
  try:
    for role in guild.roles:
      for r in roles:
        if r == str(role):
          await role.delete()
    
    for i in range(6):
      await guild.create_role(name=roles[i],colour=colours[i],hoist=True,mentionable=True)
    return True
  except: 
    return False

async def automate(client):
  while True:
    keys = db.keys()
    guild_list = db['guilds']
    for k in keys:
      if k=='guilds':
        continue
      if k in db.keys():
        data = get_rank(db[k])
        for g in guild_list:          
          await asyncio.sleep(0.1)
          if client.get_guild(int(g)) == None:
            #guild_list.remove(g)
            #db['guilds'] = guild_list
            continue
          m = client.get_guild(int(g)).get_member(int(k))
          if(m != None):
            if 'tier' in data:
              await set_role(m,data['tier'].split(' ')[0])
            elif 'error' in data and data['error']['code']==429:
              await asyncio.sleep(500)
            elif 'error' in data:
              print(data)
        await asyncio.sleep(14)
    await asyncio.sleep(5)
      
async def warn_admins(guild):
  for m in guild.members:
    if m.guild_permissions.administrator and m != guild.me:
      await m.send("Hey, I was unable to set up roles properly in " + guild.name + ".\nThis may be due to one or more roles with the same name as Brawlhalla tiers already in the server.\n\nYou can try to fix this by moving the BrawlBot above these roles and using the bb reset command.\nYou can also delete these roles and try adding BrawlBot again or use the bb reset command")

def link_steam(code):
  
  data ={
    "client_id":836287558970900540,
    "client_secret":os.environ['CLIENT_SECRET'],
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "https://BrawlBot.paulkallumkal.repl.co/login"
  }
  try:
    dKey = json.loads(requests.post('https://discord.com/api/oauth2/token',data = data).text)['access_token']
  except:
    return "An error occured"

  connections = json.loads(requests.get('https://discord.com/api/users/@me/connections', headers={"Authorization":"Bearer " + dKey}).text)
  sID=0
  for con in connections:
    if con['type']=='steam':
      sID=con['id']
      break;
  if sID==0:
    return "Please link your Steam under Discord Settings->Connections"
  
  dID = json.loads(requests.get('https://discord.com/api/users/@me',headers={"Authorization":"Bearer " + dKey}).text)['id']

  brawlID = json.loads(requests.get('https://api.brawlhalla.com/search?steamid=' + str(sID) + '&api_key=' + os.environ['API_KEY']).text)
 
  if 'brawlhalla_id' in brawlID:
    db[str(dID)]=brawlID['brawlhalla_id']
  elif 'error' in brawlID:
    return brawlID['error']['message']
  else:
    return "Brawlhalla account associated with your Steam not found"
  return "Account link successful"

def calc_glory(data):
  win1=int(data['wins'])
  win2=sum(int(row['wins']) for row in data['2v2'])
  wins=win1+win2
  peak=int(data['peak_rating'])
  if wins <= 150:
    wglory = wins*20
  else:
    wglory = 245 + 450*math.pow(math.log10(2*wins),2)
  if peak<1200:
    pglory = 250
  elif peak<1286:
    pglory = 250 + 75*(peak-1200)/8.6
  elif peak<1390:
    pglory = 1000 + 75*(peak-1286)/104.0
  elif peak<1680:
    pglory = 1870 + 113*(peak-1390)/29.0
  elif peak<2000:
    pglory = 3000 + 137*(peak-1680)/32.0
  elif peak<2300:
    pglory = 4370 + 43*(peak-2000)/30.0
  else:
    pglory = 4800 + (peak-2300)/2.0
  if wins<10:
    return "0 (You need at least 10 ranked wins to earn glory)"
  return str(int(pglory) + int(wglory))

#async def clear_roles(guild):
  #to be linked with leave command if admin wishes to remove the bot and roles associated with it