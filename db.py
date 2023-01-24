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

#single character owner checker, no longer implemented
def fetch_owner_name(charactername):
    query = 'SELECT username from characters where charactername = ?'
    for row in cur.execute(query, [charactername]):
        owner = row[0]
    print(f"query : {query} ---- values {charactername}")
    return owner

def fetch_all_owner_names():
    characterlist = []
    query = 'SELECT username, charactername from characters'
    for row in cur.execute(query):
        characterlist.append(row)
    return characterlist

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

def change_owner(charactername,owner):
    if owner == None:
        response = "Invalid owner name, please tag someone"
        return response
    if check_for_character(charactername):
        update_owner_of_character(charactername,owner)
        response = f"{charactername.upper()} has been reassigned to {owner}"
        return response
    else:
        response = "This character isn't regsitered"
        return response

#single character owner checker, no longer implemented
def check_owner(charactername):
    if check_for_character(charactername):
        owner = fetch_owner_name(charactername)
        response = f"{charactername.upper()} is registered to {owner}"
        return response
    else:
        response = "This character isn't regsitered"
        return response

#debug command to dump the entire database, no longer implemented
def debug_print_database():
    characterlist = []
    query = 'SELECT username, charactername, realm from characters'
    for row in cur.execute(query):
        characterlist.append(row)
    print(characterlist)
    return characterlist
    
