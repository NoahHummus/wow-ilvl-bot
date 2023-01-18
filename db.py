import sqlite3
import requests
import main
import json


#create connection to database file
con = sqlite3.connect('wowdb.db')
cur = con.cursor()


#save queries into variables 


#---------------------------------INSERTS--------------------------------------------------
insert_character_entry = 'INSERT into characters (username, charactername, realm) VALUES (?,?,?)'

#------------------------------------------------------------------------------------------


#---------------------------------Select--------------------------------------------------
#check_for_character = 'SELECT charactername from characters where charactername = ?'
#select_all_characters = 'SELECT charactername, realm from characters'




#-----------------------------------------------------------------------------------------

#---------------------------------Update--------------------------------------------------

#------------------------------------------------------------------------------------------

#---------------------------------Delete--------------------------------------------------

#------------------------------------------------------------------------------------------




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
    return characterlist


def insert_character(user,charactername,realm):
    query = 'INSERT into characters (username, charactername, realm) VALUES (?,?,?)'
    cur.execute(query, (str(user), charactername, realm))
    con.commit()
    print(f"query : {query} ---- values {user} {charactername} {realm}")




#specific methods
def register_character(user,charactername,realm):
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
