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

# retrieve API data for every registered character in the database
def get_all(apiPath=""):
    data = []
    urls = []
    characterlist = db.select_all_characters()
    for i in characterlist:
        charactername = i[0]
        realm = i[1]
        urls.append(f"{bnetapiuri}/profile/wow/character/{realm}/{charactername}{apiPath}?namespace=profile-us&locale=en_US&access_token={access_token}")
    data = boosted_requests(urls=urls)
    return data

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

def get_setpieces_from_profile(profilelist):
    #certainly overkill, but this is to make sure we only look at tier sets, not any set
    tierSetNames = ["Haunted Frostbrood Remains","Skybound Avenger's Flightwear","Lost Landcaller's Vesture","Scales of the Awakened","Stormwing Harrier's Camouflage","Bindings of the Crystal Scholar","Wrappings of the Waking Fist","Virtuous Silver Cataphract","Draconic Hierophant's Finery","Vault Delver's Toolkit","Elements of Infused Earth","Scalesworn Cultist's Habit","Stones of the Walking Mountain"]
    #will need to be updated as the tier sets change
    setpiecelist = []
    for response in profilelist:
        playerinfo = {}
        piecesNum = None
        pieces = response.get("equipped_item_sets")
        if pieces != None:
            #do stuff
            for sett in pieces:
                if sett['item_set']['name'] in tierSetNames:
                    piecesNum = int(sett['display_string'].split("(")[1][:-3])
            if piecesNum == None:
                piecesNum = 0
        else:
            piecesNum = 0
        charactername = response.get("character")
        charactername = charactername['name']
        playerinfo.update({'pieces': piecesNum})
        playerinfo.update({'name': charactername})
        setpiecelist.append(playerinfo)
    return setpiecelist

def build_ranking(datalist, keyToRank):
    rowlist = []
    sorteddatalist = sorted(datalist, key=itemgetter(keyToRank), reverse=True)
    for playerinfo in sorteddatalist:
        rowlist.append(f"{playerinfo.get('name')} : {playerinfo.get(keyToRank)}")
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
