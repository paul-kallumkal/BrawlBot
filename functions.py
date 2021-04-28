import json
import os
import requests
import asyncio
from replit import db
from threading import Timer

def get_data(id):
  response = requests.get('https://api.brawlhalla.com/player/' + str(id) + '/ranked?api_key=' + os.environ['API_KEY'])
  json_data = json.loads(response.text)
  if 'tier' in json_data:
    return json_data
  if 'error' in json_data:
    return 'Too many requests, try again later'
  return 'Unranked'

async def set_role(member,rank):
  roles = ['Diamond','Platinum','Gold','Silver','Bronze','Tin']
  roles.remove(rank)

  for role in member.roles:
    if(str(role) in roles):
      await member.remove_roles(role)

  for role in member.roles:
    if str(role) == rank:
      return
  
  for role in member.guild.roles:
    if(str(role) == rank):
      return await member.add_roles(role)

async def role_check(guild):
  roles = ['Diamond','Platinum','Gold','Silver','Bronze','Tin']
  colours = [0xa842ff,0x55ccff,0xffdf00,0xdadada,0xee7a0b,0xa9d3e0]
  try:
    for role in guild.roles:
      for r in roles:
        if r == str(role):
          await role.delete()
    
    for i in range(0,6):
      await guild.create_role(name=roles[i],colour=colours[i],hoist=True,mentionable=True)
    return True
  except: return False

async def automate(client):
  for i in db.keys():
    data = get_data(db[i])
    for g in client.guilds:
      if(g.id in db.keys()):
        m = g.get_member(int(i))
        if(m != None):
          if 'tier' in data:
            await set_role(m,data['tier'].split()[0])
          else:
            await set_role(m,data)
    await asyncio.sleep(15)
      
async def warn_admins(guild):
  for m in guild.members:
    if m.guild_permissions.administrator and m != guild.me:
      await m.send("BrawlBot was unable to create roles properly.\nThis may be due to one or more roles with the same name as Brawlhalla tiers already in the server.\n\nYou can try to fix this by moving the BrawlBot above these roles and using the ?reset command.\nYou can also delete these roles and try adding BrawlBot again or use the ?reset command")


#function to purge unranked players after a year