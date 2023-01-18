import requests
import db
from operator import itemgetter
import threading
import json

bneturi = 'https://us.battle.net'
bnetapiuri = 'https://us.api.blizzard.com'


# generating access token that is required in each request
def create_access_token(client_id = "c16db4e6f6844553a6ce96bd878fcda0", client_secret = "h4LrdHlSYDWJ7RAkGsavQZviPWbEVt1g"):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://us.battle.net/oauth/token', data=data, auth=(client_id, client_secret))
    jsonresponse = response.json()
    return jsonresponse.get('access_token')


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


# retrieve character profile from every registered character in the database
def get_all_characters():
    characterdata = []
    characterlist = db.select_all_characters()
    for i in characterlist:
        charactername = i[0]
        realm = i[1]
        response = get_character_profile(realm, charactername)
        characterdata.append(response.json())
    print(characterdata)
    return characterdata


def get_ilvl_from_profile(profilelist):
    ilvllist = []
    for response in profilelist:
        playerinfo = {}
        ilvl = response.get("equipped_item_level")
        print(ilvl)
        charactername = response.get("name")
        print(charactername)
        playerinfo.update({'ilvl': ilvl})
        playerinfo.update({'name': charactername})
        ilvllist.append(playerinfo)
    return ilvllist


def build_ranking(datalist):
    rowlist = []
    sorteddatalist = sorted(datalist, key=itemgetter('ilvl'), reverse=True)
    for playerinfo in sorteddatalist:
        rowlist.append(f"{playerinfo.get('name')} : {playerinfo.get('ilvl')}")
    text = '\n'.join(rowlist)
    print(text)
    return text









