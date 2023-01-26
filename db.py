import sqlite3
import requests
import main
import json

#create connection to database file
con = sqlite3.connect('wowdb.db')
cur = con.cursor()

#base methods
def check_for_character(charactername):
    query = 'SELECT charactername from characters where charactername = ?'
    cur.execute(query, [charactername])
    result = cur.fetchone() 
    return result

def select_all_characters():
    characterlist = []
    query = 'SELECT charactername, realm from characters'
    for row in cur.execute(query):
        characterlist.append(row)
    print(characterlist)
    print(type(characterlist[0]))
    return characterlist

def insert_character(user,charactername,realm):
    query = 'INSERT into characters (username, charactername, realm) VALUES (?,?,?)'
    cur.execute(query, (str(user), charactername, realm))
    con.commit()
    print(f"query : {query} ---- values {user} {charactername} {realm}")

def update_owner_of_character(charactername,owner):
    query = 'UPDATE characters SET username = ? where charactername = ?'
    cur.execute(query, (str(owner), charactername))
    con.commit()
    print(f"query : {query} ---- values {owner} {charactername}")
    
def update_character_mythic_prog(charactername,newscore):
    query = 'UPDATE characters SET last_mythic_score = ? where charactername = ?'
    cur.execute(query, (int(newscore), charactername))
    con.commit()
    print(f"query : {query} ---- values {newscore} {charactername}")

def update_character_ilvl_prog(charactername,newilvl):
    query = 'UPDATE characters SET last_ilvl = ? where charactername = ?'
    cur.execute(query, (int(newilvl), charactername))
    con.commit()
    print(f"query : {query} ---- values {newilvl} {charactername}")

def fetch_all_owner_names():
    characterlist = []
    query = 'SELECT username, charactername from characters'
    for row in cur.execute(query):
        characterlist.append(row)
    return characterlist
    
def get_last_mythic_by_player(charactername):
    query = 'SELECT last_mythic_score from characters where charactername = ?'
    cur.execute(query, [charactername])
    result = cur.fetchone()
    print(charactername,"result",result)
    return result[0]

def get_last_ilvl_by_player(charactername):
    query = 'SELECT last_ilvl from characters where charactername = ?'
    cur.execute(query, [charactername])
    result = cur.fetchone()
    print(charactername,"result",result)
    return result[0]

#specific methods
def register_character(user,charactername,realm):
    realm = realm.replace(" ", "-").replace("'", "").replace("`", "")
    #checks if the character exists - looking for anything but a sucess on the wow api character lookup
    if main.get_character_profile(realm,charactername).status_code != 200:
        response = "Can't locate this character - Unable to register"
        return response
    #checks if the character is already registered in the local database
    if check_for_character(charactername):
        response = "This character is already registered"
        return response
    insert_character(user,charactername,realm)
    response = f"{charactername.upper()} has been registered!"
    return response

#weekly db update for progging
def update_prog_log():
    print("updating prog log, in db")
    mythiclist = main.get_mythic_from_profile(main.get_all('/mythic-keystone-profile'))
    for character in mythiclist:
        update_character_mythic_prog(character['name'].lower(),character['mythic'])
    ilvllist = main.get_ilvl_from_profile(main.get_all())
    for character in ilvllist:
        update_character_ilvl_prog(character['name'].lower(),character['ilvl'])