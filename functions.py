import json
import os
import requests
from replit import db

def get_data(id):
  response = requests.get('https://api.brawlhalla.com/player/' + str(id) + '/ranked?api_key=' + os.environ['API_KEY'])
  json_data = json.loads(response.text)
  if 'tier' in json_data:
    return json_data
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

async def roll_check(client):
  roles = ['Diamond','Platinum','Gold','Silver','Bronze','Tin']


#function to purge unranked players after a month