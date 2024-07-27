import os
import sqlite3
import time
from functools import lru_cache
from typing import Dict, Any

import aiohttp
import requests
from dotenv import load_dotenv

import db
from operator import itemgetter
from request_boost import boosted_requests


load_dotenv()

bneturi = 'https://us.battle.net'
bnetapiuri = 'https://us.api.blizzard.com'
REGION = 'us'

# generating access token that is required in each request
def create_access_token(client_id = os.getenv("CLIENT_ID"), client_secret = os.getenv("CLIENT_SECRET")):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://us.battle.net/oauth/token', data=data, auth=(client_id, client_secret))
    jsonresponse = response.json()
    return jsonresponse.get('access_token')

#generate token once on startup
access_token = create_access_token()

# retrieve character profile from wow api
def get_character_profile(realm,charactername):
    print("getting profile for: "+charactername)
    print("realm: "+realm)
    response = requests.get(f"{bnetapiuri}/profile/wow/character/{realm}/{charactername}?namespace=profile-us&locale=en_US&access_token={access_token}")
    return response


def extract_duel_relevant_data(character_data):
    # Basic character information
    basic_info = {
        "name": character_data.get("name", "Unknown"),
        "level": character_data.get("level", 0),
        "class": character_data.get("character_class", {}).get("name", "Unknown"),
        "race": character_data.get("race", {}).get("name", "Unknown"),
        "faction": character_data.get("faction", {}).get("name", "Unknown"),
        "gender": character_data.get("gender", {}).get("name", "Unknown"),
        "realm": character_data.get("realm", {}).get("name", "Unknown"),
        "average_item_level": character_data.get("average_item_level", 0),
        "equipped_item_level": character_data.get("equipped_item_level", 0),
        "achievement_points": character_data.get("achievement_points", 0),
        "last_login_timestamp": character_data.get("last_login_timestamp", 0),
    }

    # Guild information
    guild_info = {
        "name": character_data.get("guild", {}).get("name", "None"),
        "realm": character_data.get("guild", {}).get("realm", {}).get("name", "Unknown"),
    } if "guild" in character_data else None

    # Covenant information
    covenant_info = {
        "name": character_data.get("covenant_progress", {}).get("chosen_covenant", {}).get("name", "Unknown"),
        "renown_level": character_data.get("covenant_progress", {}).get("renown_level", 0),
    } if "covenant_progress" in character_data else None

    # Active specialization
    # Abilities (talents)
    abilities = []
    specialization_data = character_data.get('specializations', {})
    specializations = specialization_data.get('specializations', [])
    specialization_name = specialization_data.get('active_specialization', {}).get('name', {}).get('en_US', 'Unknown')
    if specializations:
        specialization_name = specializations[0].get('name', {}).get('en_US', 'Unknown')
        loadouts = specializations[0].get('loadouts', [])
        if loadouts:
            class_talents = loadouts[0].get('selected_class_talents')
            for talent in class_talents:
                spell = talent.get('spell_tooltip', {}).get('spell', {})
                if spell:
                    abilities.append({
                        'name': spell.get('name', ''),
                        'description': talent.get('spell_tooltip', {}).get('description', '')
                    })
            spec_talents = loadouts[0].get('selected_spec_talents')
            for talent in spec_talents:

                spell = talent.get('spell_tooltip', {}).get('spell', {})
                if spell:
                    abilities.append({
                        'name': spell.get('name', ''),
                        'description': talent.get('spell_tooltip', {}).get('description', '')
                    })

    active_spec_info = {
        "name": specialization_name,
    }

    # Statistics
    statistics_data = character_data.get('statistics', {})
    stats = {
        "health": statistics_data.get("health", 0),
        "power": {
            "type": statistics_data.get("power_type", {}).get("name", {}).get("en_US", "Unknown"),
            "amount": statistics_data.get("power", 0)
        },
        "strength": statistics_data.get("strength", {}).get("effective", 0),
        "agility": statistics_data.get("agility", {}).get("effective", 0),
        "intellect": statistics_data.get("intellect", {}).get("effective", 0),
        "stamina": statistics_data.get("stamina", {}).get("effective", 0),
        "melee_crit": statistics_data.get("melee_crit", {}).get("value", 0),
        "melee_haste": statistics_data.get("melee_haste", {}).get("value", 0),
        "mastery": statistics_data.get("mastery", {}).get("value", 0),
        "bonus_armor": statistics_data.get("bonus_armor", 0),
        "lifesteal": statistics_data.get("lifesteal", {}).get("value", 0),
        "versatility": statistics_data.get("versatility", 0),
        "avoidance": statistics_data.get("avoidance", {}).get("value", 0),
        "attack_power": statistics_data.get("attack_power", 0),
        "main_hand_damage_min": statistics_data.get("main_hand_damage_min", 0),
        "main_hand_damage_max": statistics_data.get("main_hand_damage_max", 0),
        "main_hand_speed": statistics_data.get("main_hand_speed", 0),
        "main_hand_dps": statistics_data.get("main_hand_dps", 0),
    }

    # Equipment
    equipment = []
    for item in character_data.get('equipment', {}).get('equipped_items', []):
        equipment.append({
            "name": item.get("name", {}).get("en_US", "Unknown"),
            "slot": item.get("slot", {}).get("name", {}).get("en_US", "Unknown"),
            "item_level": item.get("level", {}).get("value", 0),
            "quality": item.get("quality", {}).get("name", {}).get("en_US", "Unknown"),
        })

    # Achievements (just count for now, you can expand this if needed)
    achievements_count = len(character_data.get('achievements', {}).get('achievements', []))

    # Media (character render)
    character_media = character_data.get('media', {}).get('assets', [])
    character_render = next((asset['value'] for asset in character_media if asset['key'] == 'main-raw'), None)

    return {
        "basic_info": basic_info,
        "guild_info": guild_info,
        "covenant_info": covenant_info,
        "active_spec": active_spec_info,
        "abilities": abilities,
        "stats": stats,
        "equipment": equipment,
        "achievements_count": achievements_count,
        "character_render": character_render,
    }

@lru_cache(maxsize=128)
def get_all_character_data(realm, character_name):
    headers = {'Authorization': f'Bearer {access_token}'}

    # Get basic character data
    character_url = f'https://us.api.blizzard.com/profile/wow/character/{realm}/{character_name.lower()}?namespace=profile-us&locale=en_US'
    character_response = requests.get(character_url, headers=headers)

    if character_response.status_code != 200:
        return None

    character_data = character_response.json()

    # Get additional data (equipment, achievements, etc.)
    equipment_url = character_data.get('equipment', {}).get('href')
    achievements_url = character_data.get('achievements', {}).get('href')
    media_url = character_data.get('media', {}).get('href')

    # Get specialization data
    spec_url = character_data.get('specializations', {}).get('href')
    stat_url = character_data.get('statistics', {}).get('href')

    equipment_response = requests.get(equipment_url, headers=headers)
    achievements_response = requests.get(achievements_url, headers=headers)
    spec_response = requests.get(spec_url, headers=headers)
    stat_response = requests.get(stat_url, headers=headers)
    media_response = requests.get(media_url, headers=headers)


    if equipment_response.status_code == 200:
        character_data['equipment'] = equipment_response.json()

    if achievements_response.status_code == 200:
        character_data['achievements'] = achievements_response.json()

    if spec_response.status_code == 200:
        character_data['specializations'] = spec_response.json()

    if stat_response.status_code == 200:
        character_data['statistics'] = stat_response.json()

    if media_response.status_code == 200:
        character_data['media'] = media_response.json()

    return character_data


async def get_character_raid_profile(realm, charactername):
    base_url = f"https://us.api.blizzard.com/profile/wow/character/{realm}/{charactername}"

    # Fetch basic profile
    profile_url = f"{base_url}?namespace=profile-us&locale=en_US&access_token={access_token}"
    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url) as response:
            if response.status == 200:
                profile_data = await response.json()
            else:
                return None

    # Fetch encounters data
    encounters_url = f"{base_url}/encounters/raids?namespace=profile-us&locale=en_US&access_token={access_token}"
    async with aiohttp.ClientSession() as session:
        async with session.get(encounters_url) as response:
            if response.status == 200:
                encounters_data = await response.json()
            else:
                encounters_data = None

    return {"profile": profile_data, "encounters": encounters_data}
# retrieve API data for every registered character in the database
def get_all(apiPath=""):
    data = []
    urls = []
    characterlist = db.select_all_characters()
    for i in characterlist:
        charactername = i[0]
        realm = i[1]
        urlTemp = f"{bnetapiuri}/profile/wow/character/{realm}/{charactername}{apiPath}?namespace=profile-us&locale=en_US&access_token={access_token}"
        urlNewTemp = urlTemp.replace("\u00E1","%C3%A1")
        urls.append(urlNewTemp)
    print("I'm goin in !!!'")
    data = boosted_requests(urls=urls)
    print("we outtie")
    return data

#wow it actually checks if wow is down (technically it checks Kul Tiras directly)
def isWowDown():
    response = requests.get(f"https://us.api.blizzard.com/data/wow/connected-realm/1147?namespace=dynamic-us&locale=en_US&access_token={access_token}")
    status = response.json().get('status')
    status = status['type']
    return status=="DOWN"

#fetch info for chatgpt eulogy
def fetch_euology_data(charactername):
    print(charactername)
    print(db.check_character_realm(charactername))
    print(get_character_profile(db.check_character_realm(charactername),charactername))
    euology_data = {}
    response = get_character_profile(db.check_character_realm(charactername),charactername)
    j = response.json()
    name = j.get('name')
    if j.get('active_title') == None:
        euology_data.update({'name': j.get('name')})
    else:
        euology_data.update({'name': j.get('active_title')['display_string'].format(name=name)})
    euology_data.update({'race': j.get('race')['name']})
    euology_data.update({'class': j.get('character_class')['name']})
    euology_data.update({'spec': j.get('active_spec')['name']})
    euology_data.update({'realm': j.get('realm')['name']})
    euology_data.update({'gender': j.get('gender')['name']})
    return euology_data

def get_ilvl_from_profile(profilelist):
    ilvllist = []
    for response in profilelist:
        playerinfo = {}
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

def get_mythicprog_from_profile(profilelist):
    proglist = []
    for response in profilelist:
        playerinfo = {}
        mythic = response.get("current_mythic_rating")
        if mythic != None:
            mythic = int(mythic['rating'])
            charactername = response.get("character")
            charactername = charactername['name']
            last = db.get_last_mythic_by_player(charactername.lower())
            print(charactername,"last",last)
            if last != None:
                progVal = mythic-last
                if progVal != 0:
                    if last != 0:
                        progcentage = round(((progVal/last)*100),2)
                        rankString = f"{progVal} (+{progcentage}%)"
                        prog = progVal
                    else:
                        rankString = f"{mythic} (+infinity%)"
                        prog = mythic
                else:
                    rankString = "0"
                    prog = 0
            else:
                rankString = "<unknown>"
                prog = -659
            playerinfo.update({'rankString': rankString})
            playerinfo.update({'prog': prog})
            playerinfo.update({'name': charactername})
            proglist.append(playerinfo)
        else:
            progVal = 0
            rankString = f"{progVal}"
            prog = 0
            charactername = response.get("character")
            charactername = charactername['name']
            playerinfo.update({'rankString': rankString})
            playerinfo.update({'prog': prog})
            playerinfo.update({'name': charactername})
            proglist.append(playerinfo)
    return proglist


def get_ilvlprog_from_profile(profilelist):
    proglist = []
    for response in profilelist:
        playerinfo = {}
        ilvl = response.get("average_item_level")
        charactername = response.get("name")
        last = db.get_last_ilvl_by_player(charactername.lower())
        if last != None:
            prog = ilvl-last
        else:
            prog = -659
        playerinfo.update({'prog': prog})
        playerinfo.update({'name': charactername})
        proglist.append(playerinfo)
    return proglist

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
    print(f"\ndatalist:{datalist}")
    print(f"\nkeyToRank:{keyToRank}")
    sorteddatalist = sorted(datalist, key=itemgetter(keyToRank), reverse=True)
    if "rankString" in datalist[0].keys():
        for playerinfo in sorteddatalist:
            rowlist.append(f"{playerinfo.get('name')} : {playerinfo.get('rankString')}")
    else:
        for playerinfo in sorteddatalist:
            rowlist.append(f"{playerinfo.get('name')} : {playerinfo.get(keyToRank)}")
    text = '\n'.join(rowlist)
    text = text.replace("-659","<unknown>")
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



# Blizzard API functions
def get_character_raid_progress(character: str, realm: str) -> Dict[str, Any]:
    url = f"{bnetapiuri}/profile/wow/character/{realm}/{character}/encounters/raids?namespace=profile-{REGION}&locale=en_US&access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching raid progress for {character}-{realm}: {response.status_code}")
    return None


def get_item_subclasses(item_class_id):
    url = f"https://us.api.blizzard.com/data/wow/item-class/{item_class_id}?namespace=static-us&locale=en_US&access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('item_subclasses', [])
    else:
        print(f"Error fetching item subclasses for class {item_class_id}: {response.status_code}")
        return []


def populate_transmog_items():
    print("Populating transmog items...")
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    base_url = f"https://us.api.blizzard.com/data/wow/search/item?namespace=static-us&locale=en_US&orderby=id&_pageSize=1000&access_token={access_token}"

    items_processed = 0
    transmog_items_added = 0
    start_time = time.time()

    # We'll search in chunks of 100,000 item IDs
    chunk_size = 100000
    start_id = 1
    end_id = start_id + chunk_size - 1

    while True:
        url = f"{base_url}&id=[{start_id},{end_id}]"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error fetching items: {response.status_code}")
            break

        data = response.json()
        results = data.get('results', [])

        if not results:
            print(f"No items found in range {start_id}-{end_id}.")
            # Move to the next chunk
            start_id = end_id + 1
            end_id = start_id + chunk_size - 1
            if start_id > 1000000:  # Arbitrary upper limit, adjust as needed
                print("Reached upper item ID limit. Stopping search.")
                break
            continue

        for item in results:
            item_data = item['data']
            item_id = item_data['id']
            name = item_data['name']['en_US']

            # Check if the item is a weapon or armor
            item_class = item_data.get('item_class', {}).get('name', {}).get('en_US')
            if item_class not in ['Weapon', 'Armor']:
                continue

            quality = item_data['quality']['type']
            inventory_type = item_data.get('inventory_type', {}).get('name', {}).get('en_US', 'Unknown')

            # Skip items with unwanted inventory types
            if inventory_type in ['Bag', 'Tabard', 'Shirt', 'Non-equippable']:
                continue

            icon = item_data.get('media', {}).get('id', 'unknown')

            cur.execute('''
            INSERT OR IGNORE INTO transmog_items (item_id, name, slot, quality, icon)
            VALUES (?, ?, ?, ?, ?)
            ''', (item_id, name, inventory_type, quality, icon))

            transmog_items_added += cur.rowcount
            items_processed += 1

        elapsed_time = time.time() - start_time
        print(
            f"Processed items {start_id}-{end_id}: Added {transmog_items_added} transmog items in {elapsed_time:.2f} seconds")

        # Commit after each chunk to avoid losing all data if an error occurs
        con.commit()

        # Move to the next chunk
        start_id = end_id + 1
        end_id = start_id + chunk_size - 1

        # Respect rate limits
        time.sleep(0.1)

    con.close()
    total_time = time.time() - start_time
    print(
        f"Transmog items population complete. Processed {items_processed} items, added {transmog_items_added} transmog items in {total_time:.2f} seconds")