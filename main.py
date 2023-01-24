import requests
import db
from operator import itemgetter
from request_boost import boosted_requests
import json

bneturi = 'https://us.battle.net'
bnetapiuri = 'https://us.api.blizzard.com'

# generating access token that is required in each request
def create_access_token(client_id = "c16db4e6f6844553a6ce96bd878fcda0", client_secret = "h4LrdHlSYDWJ7RAkGsavQZviPWbEVt1g"):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://us.battle.net/oauth/token', data=data, auth=(client_id, client_secret))
    jsonresponse = response.json()
    return jsonresponse.get('access_token')

#generate token once on startup
access_token = create_access_token()

### DEPRECATED ###
# retrieve character profile from wow api
def get_character_profile(realm,charactername):
    headers = {
    'Authorization' : f"BEARER {create_access_token()}"
    }
    params = {
    'namespace' : 'profile-us',
    'locale' : 'en_US'
    }
    response = requests.get(f"{bnetapiuri}/profile/wow/character/{realm}/{charactername}", params=params, headers=headers)
    print(f"Status code : {response.status_code}")
    print(response.json())
    return response

### DEPRECATED ###
# retrieve character profile from every registered character in the database
def get_all_characters():
    characterdata = []
    characterlist = db.select_all_characters()
    for i in characterlist:
        charactername = i[0]
        realm = i[1]
        response = get_character_profile(realm, charactername)
        #response = get_character_items(realm, charactername)
        characterdata.append(response.json())
    print(characterdata)
    return characterdata

# retrieve character profile from every registered character in the database
def threaded_get_all_characters():
    characterdata = []
    characterlist = db.select_all_characters()
    urls = []
    for i in characterlist:
        charactername = i[0]
        realm = i[1]
        urls.append(f"{bnetapiuri}/profile/wow/character/{realm}/{charactername}?namespace=profile-us&locale=en_US&access_token={access_token}")
    characterdata = boosted_requests(urls=urls)
    return characterdata

# retrieve mythic profile from every registered character in the database
def threaded_get_all_mythics():
    characterdata = []
    characterlist = db.select_all_characters()
    urls = []
    for i in characterlist:
        charactername = i[0]
        realm = i[1]
        urls.append(f"{bnetapiuri}/profile/wow/character/{realm}/{charactername}/mythic-keystone-profile?namespace=profile-us&locale=en_US&access_token={access_token}")
    characterdata = boosted_requests(urls=urls)
    return characterdata

def get_ilvl_from_profile(profilelist):
    ilvllist = []
    for response in profilelist:
        playerinfo = {}
        #ilvl = response.get("equipped_item_level")
        ilvl = response.get("average_item_level")
        charactername = response.get("name")
        playerinfo.update({'ilvl': ilvl})
        playerinfo.update({'name': charactername})
        ilvllist.append(playerinfo)
    return ilvllist

def get_mythic_from_profile(profilelist):
    mythiclist = []
    for response in profilelist:
        playerinfo = {}
        mythic = response.get("current_mythic_rating")
        if mythic != None:
            mythic = int(mythic['rating'])
            charactername = response.get("character")
            charactername = charactername['name']
            playerinfo.update({'mythic': mythic})
            playerinfo.update({'name': charactername})
            mythiclist.append(playerinfo)
        else:
            mythic = 0
            charactername = response.get("character")
            charactername = charactername['name']
            playerinfo.update({'mythic': mythic})
            playerinfo.update({'name': charactername})
            mythiclist.append(playerinfo)
    return mythiclist

def build_ranking(datalist):
    rowlist = []
    sorteddatalist = sorted(datalist, key=itemgetter('ilvl'), reverse=True)
    for playerinfo in sorteddatalist:
        rowlist.append(f"{playerinfo.get('name')} : {playerinfo.get('ilvl')}")
    text = '\n'.join(rowlist)
    print(text)
    return text

def build_ranking_mythic(datalist):
    rowlist = []
    sorteddatalist = sorted(datalist, key=itemgetter('mythic'), reverse=True)
    for playerinfo in sorteddatalist:
        rowlist.append(f"{playerinfo.get('name')} : {playerinfo.get('mythic')}")
    text = '\n'.join(rowlist)
    print(text)
    return text

def list_owners():
    rowlist = []
    data = db.fetch_all_owner_names()
    for item in data:
        rowlist.append(f"{item[1].capitalize()} : {item[0]}")
    text = '\n'.join(rowlist)
    print(text)
    return text
