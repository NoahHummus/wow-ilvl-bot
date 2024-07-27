import random
import sqlite3
from datetime import datetime

import requests
import main
import json

from raid_shit import CURRENT_RAID

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

def unregister_character(charactername):
    query = 'DELETE from characters WHERE charactername = ?'
    cur.execute(query, [charactername])
    con.commit()
    print(f"query : {query} ---- values {charactername}")


def update_owner_of_character(charactername,owner):
    query = 'UPDATE characters SET username = ? where charactername = ?'
    cur.execute(query, (str(owner), charactername))
    con.commit()
    print(f"query : {query} ---- values {owner} {charactername}")

def fetch_all_owner_names():
    characterlist = []
    query = 'SELECT username, charactername from characters'
    for row in cur.execute(query):
        characterlist.append(row)
    return characterlist
       
def check_character_realm(charactername):
    query = 'SELECT realm from characters where charactername = ?'
    cur.execute(query, [charactername])
    result = cur.fetchone()
    return result[0]
    
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
    
def get_weeks_since_mythic_prog(charactername):
    query = 'SELECT weeks_since_mythic_prog from characters where charactername = ?'
    cur.execute(query, [charactername])
    result = cur.fetchone()
    print(charactername,"result",result)
    return result[0]

def set_weeks_since_mythic_prog(charactername, weekVal):
    query = 'UPDATE characters SET weeks_since_mythic_prog = ? where charactername = ?'
    cur.execute(query, (weekVal, charactername))
    con.commit()
    print(f"query : {query} ---- values {weekVal} {charactername}")

def get_weeks_since_ilvl_prog(charactername):
    query = 'SELECT weeks_since_ilvl_prog from characters where charactername = ?'
    cur.execute(query, [charactername])
    result = cur.fetchone()
    print(charactername,"result",result)
    return result[0]

def set_weeks_since_ilvl_prog(charactername, weekVal):
    query = 'UPDATE characters SET weeks_since_ilvl_prog = ? where charactername = ?'
    cur.execute(query, (weekVal, charactername))
    con.commit()
    print(f"query : {query} ---- values {weekVal} {charactername}")

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
        print("updating mythic of:"+character['name'].lower())
        update_character_mythic_prog(character['name'].lower(),character['mythic'])
    ilvllist = main.get_ilvl_from_profile(main.get_all())
    for character in ilvllist:
        print("updating ilvl of :"+character['name'].lower())
        update_character_ilvl_prog(character['name'].lower(),character['ilvl'])
        #after setting mythic+ilvl prog, check weeks. unregister if non-progger
        nonprogLimit = 2
        if (get_weeks_since_ilvl_prog(character)>=nonprogLimit and get_weeks_since_mythic_prog(character)>=nonprogLimit):
            print(f"!!! {character} is a NONPROGGER, unregistering")
            unregister_character(character)

def update_character_mythic_prog(charactername,newscore):
    if newscore == get_last_mythic_by_player(charactername):
        print(f"{charactername} did not prog in mythic this week")
        set_weeks_since_mythic_prog(charactername,int(get_weeks_since_mythic_prog(charactername))+1)
    else:
        print(f"{charactername} progged in mythic this week")
        set_weeks_since_mythic_prog(charactername,0)
    query = 'UPDATE characters SET last_mythic_score = ? where charactername = ?'
    cur.execute(query, (int(newscore), charactername))
    con.commit()
    print(f"query : {query} ---- values {newscore} {charactername}")

def update_character_ilvl_prog(charactername,newilvl):
    if newilvl == get_last_ilvl_by_player(charactername):
        print(f"{charactername} did not prog in ilvl this week")
        set_weeks_since_ilvl_prog(charactername,int(get_weeks_since_ilvl_prog(charactername))+1)
    else:
        print(f"{charactername} progged in ilvl this week")
        set_weeks_since_ilvl_prog(charactername,0)
    query = 'UPDATE characters SET last_ilvl = ? where charactername = ?'
    cur.execute(query, (int(newilvl), charactername))
    con.commit()
    print(f"query : {query} ---- values {newilvl} {charactername}")


def get_registered_characters():
    query = 'SELECT charactername, realm FROM characters'
    cur.execute(query)
    results = cur.fetchall()
    return [{'name': row[0], 'realm': row[1]} for row in results]


def save_character_render(character_name, render_url):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('''
    INSERT OR REPLACE INTO character_renders (character_name, render_url)
    VALUES (?, ?)
    ''', (character_name, render_url))

    con.commit()
    con.close()

def update_raid_progress(character, realm, progress):
    # First, update the last_raid_update in the characters table
    update_query = 'UPDATE characters SET last_raid_update = ? WHERE charactername = ?'
    cur.execute(update_query, (datetime.now(), character))

    # Check if a record exists for this character and raid
    check_query = 'SELECT id FROM raid_progress WHERE charactername = ? AND raid_name = ?'
    cur.execute(check_query, (character, progress['name']))
    existing_record = cur.fetchone()

    if existing_record:
        # Update existing record
        update_query = '''
        UPDATE raid_progress
        SET normal_progress = ?, heroic_progress = ?, mythic_progress = ?,
            last_killed_boss = ?, last_kill_timestamp = ?
        WHERE id = ?
        '''
        cur.execute(update_query, (
            progress['normal_progress'],
            progress['heroic_progress'],
            progress['mythic_progress'],
            progress['last_killed_boss'],
            progress['last_kill_timestamp'],
            existing_record[0]
        ))
    else:
        # Insert new record
        insert_query = '''
        INSERT INTO raid_progress (charactername, raid_name, normal_progress, heroic_progress,
                                   mythic_progress, last_killed_boss, last_kill_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(insert_query, (
            character,
            progress['name'],
            progress['normal_progress'],
            progress['heroic_progress'],
            progress['mythic_progress'],
            progress['last_killed_boss'],
            progress['last_kill_timestamp']
        ))

    con.commit()

def get_raid_progress(character, realm):
    query = '''
    SELECT raid_name, normal_progress, heroic_progress, mythic_progress,
           last_killed_boss, last_kill_timestamp
    FROM raid_progress
    WHERE charactername = ?
    ORDER BY last_kill_timestamp DESC
    LIMIT 1
    '''
    cur.execute(query, (character,))
    result = cur.fetchone()

    if result:
        return {
            'name': result[0],
            'normal_progress': result[1],
            'heroic_progress': result[2],
            'mythic_progress': result[3],
            'last_killed_boss': result[4],
            'last_kill_timestamp': datetime.fromisoformat(result[5]) if result[5] else None
        }
    else:
        return None


def get_all_raid_progress():
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('''
    SELECT character_name, realm, raid_name, lfr_progress, normal_progress, heroic_progress, mythic_progress, last_updated
    FROM raid_progress
    ORDER BY (lfr_progress + normal_progress + heroic_progress + mythic_progress) DESC
    ''')

    rows = cur.fetchall()
    con.close()

    progress_data = []
    for row in rows:
        progress_data.append({
            'character_name': row[0],
            'realm': row[1],
            'raid_name': row[2],
            'lfr_progress': row[3],
            'normal_progress': row[4],
            'heroic_progress': row[5],
            'mythic_progress': row[6],
            'last_updated': row[7]
        })

    return progress_data


def get_raid_participation():
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    current_raid = CURRENT_RAID["name"]
    if not current_raid:
        return None, None

    # Get participants
    cur.execute('''
    SELECT character_name, realm, lfr_progress, normal_progress, heroic_progress, mythic_progress
    FROM raid_progress
    WHERE raid_name = ? AND (lfr_progress > 0 OR normal_progress > 0 OR heroic_progress > 0 OR mythic_progress > 0)
    ORDER BY (lfr_progress + normal_progress + heroic_progress + mythic_progress) DESC
    ''', (current_raid,))

    participants = cur.fetchall()

    # Get non-participants
    cur.execute('''
    SELECT c.charactername, c.realm
    FROM characters c
    LEFT JOIN raid_progress rp ON c.charactername = rp.character_name AND c.realm = rp.realm AND rp.raid_name = ?
    WHERE rp.character_name IS NULL OR (rp.lfr_progress = 0 AND rp.normal_progress = 0 AND rp.heroic_progress = 0 AND rp.mythic_progress = 0)
    ''', (current_raid,))

    non_participants = cur.fetchall()

    con.close()

    return participants, non_participants


def get_current_raid_progress():
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    current_raid = CURRENT_RAID["name"]
    cur.execute('''
    SELECT character_name, realm, raid_name, lfr_progress, normal_progress, heroic_progress, mythic_progress, last_updated
    FROM raid_progress
    WHERE raid_name = ?
    ORDER BY (lfr_progress + normal_progress + heroic_progress + mythic_progress) DESC
    ''', (current_raid,))

    rows = cur.fetchall()
    con.close()

    progress_data = []
    for row in rows:
        progress_data.append({
            'character_name': row[0],
            'realm': row[1],
            'raid_name': row[2],
            'lfr_progress': row[3],
            'normal_progress': row[4],
            'heroic_progress': row[5],
            'mythic_progress': row[6],
            'last_updated': row[7]
        })

    return progress_data

def get_random_item(slot):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('SELECT item_id, name, quality, icon FROM transmog_items WHERE slot = ? ORDER BY RANDOM() LIMIT 1',
                (slot,))
    result = cur.fetchone()

    con.close()
    return result


def generate_random_transmog_set():
    armor_slots = ['Head', 'Shoulder', 'Back', 'Chest', 'Wrist', 'Hands', 'Waist', 'Legs', 'Feet']
    weapon_slots = ['Two-Hand', 'Ranged', 'One-Hand', 'Off Hand', 'Held in Off-hand']

    set_items = {}

    # Add armor items
    for slot in armor_slots:
        item = get_random_item(slot)
        if item:
            set_items[slot] = item

    # Add weapon(s)
    weapon_choice = random.choice(weapon_slots)
    if weapon_choice == 'Two-Hand' or weapon_choice == 'Ranged':
        item = get_random_item(weapon_choice)
        if item:
            set_items[weapon_choice] = item
    elif weapon_choice == 'One-Hand':
        main_hand = get_random_item('One-Hand')
        if main_hand:
            set_items['Main Hand'] = main_hand
        off_hand_choice = random.choice(['Off Hand', 'Held in Off-hand', None])
        if off_hand_choice:
            off_hand = get_random_item(off_hand_choice)
            if off_hand:
                set_items[off_hand_choice] = off_hand
    else:  # 'Off Hand' or 'Held in Off-hand'
        main_hand = get_random_item('One-Hand')
        if main_hand:
            set_items['Main Hand'] = main_hand
        off_hand = get_random_item(weapon_choice)
        if off_hand:
            set_items[weapon_choice] = off_hand

    return set_items


def get_transmog_set(set_id):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('''
    SELECT ts.*, 
           ti_head.name as head_name, ti_head.icon as head_icon,
           ti_shoulder.name as shoulder_name, ti_shoulder.icon as shoulder_icon,
           ti_back.name as back_name, ti_back.icon as back_icon,
           ti_chest.name as chest_name, ti_chest.icon as chest_icon,
           ti_wrist.name as wrist_name, ti_wrist.icon as wrist_icon,
           ti_hands.name as hands_name, ti_hands.icon as hands_icon,
           ti_waist.name as waist_name, ti_waist.icon as waist_icon,
           ti_legs.name as legs_name, ti_legs.icon as legs_icon,
           ti_feet.name as feet_name, ti_feet.icon as feet_icon,
           ti_main_hand.name as main_hand_name, ti_main_hand.icon as main_hand_icon,
           ti_off_hand.name as off_hand_name, ti_off_hand.icon as off_hand_icon
    FROM transmog_sets ts
    LEFT JOIN transmog_items ti_head ON ts.head_id = ti_head.id
    LEFT JOIN transmog_items ti_shoulder ON ts.shoulder_id = ti_shoulder.id
    LEFT JOIN transmog_items ti_back ON ts.back_id = ti_back.id
    LEFT JOIN transmog_items ti_chest ON ts.chest_id = ti_chest.id
    LEFT JOIN transmog_items ti_wrist ON ts.wrist_id = ti_wrist.id
    LEFT JOIN transmog_items ti_hands ON ts.hands_id = ti_hands.id
    LEFT JOIN transmog_items ti_waist ON ts.waist_id = ti_waist.id
    LEFT JOIN transmog_items ti_legs ON ts.legs_id = ti_legs.id
    LEFT JOIN transmog_items ti_feet ON ts.feet_id = ti_feet.id
    LEFT JOIN transmog_items ti_main_hand ON ts.main_hand_id = ti_main_hand.id
    LEFT JOIN transmog_items ti_off_hand ON ts.off_hand_id = ti_off_hand.id
    WHERE ts.id = ?
    ''', (set_id,))

    result = cur.fetchone()
    con.close()

    return result


def vote_transmog(set_id, user_id, vote):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('''
    INSERT OR REPLACE INTO transmog_votes (set_id, user_id, vote)
    VALUES (?, ?, ?)
    ''', (set_id, user_id, vote))

    con.commit()
    con.close()


def get_transmog_votes(set_id):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('''
    SELECT SUM(CASE WHEN vote = 1 THEN 1 ELSE 0 END) as upvotes,
           SUM(CASE WHEN vote = -1 THEN 1 ELSE 0 END) as downvotes
    FROM transmog_votes
    WHERE set_id = ?
    ''', (set_id,))

    result = cur.fetchone()
    con.close()

    return {'upvotes': result[0] or 0, 'downvotes': result[1] or 0}


def get_all_registered_characters():
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    cur.execute('SELECT charactername, realm FROM characters')
    characters = cur.fetchall()
    con.close()
    return characters


def get_raid_characters_to_update():
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    today = datetime.now().date().isoformat()

    cur.execute('''
    SELECT c.charactername, c.realm
    FROM characters c
    LEFT JOIN raid_progress rp ON c.charactername = rp.character_name AND c.realm = rp.realm
    WHERE rp.last_updated IS NULL OR DATE(rp.last_updated) < ?
    ''', (today,))

    characters = cur.fetchall()
    con.close()

    return characters

def drop_raid_progress_table():
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    try:
        cur.execute('DROP TABLE IF EXISTS raid_progress')
        print("raid_progress table dropped successfully.")
    except sqlite3.Error as e:
        print(f"Error dropping raid_progress table: {e}")
    finally:
        con.commit()
        con.close()


def save_trivia_score(username, score):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('INSERT INTO trivia_scores (username, score) VALUES (?, ?)', (username, score))

    con.commit()
    con.close()


def add_trivia_question(question, answers, correct_index, difficulty, image_url=None):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    try:
        cur.execute('''
        INSERT INTO trivia_questions (question, answers, correct_index, difficulty, image_url)
        VALUES (?, ?, ?, ?, ?)
        ''', (question, json.dumps(answers), correct_index, difficulty, image_url))
        con.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        con.close()


def get_character_render(character_name):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('SELECT render_url FROM character_renders WHERE character_name = ?', (character_name,))
    result = cur.fetchone()

    con.close()

    return result[0] if result else None


def get_duel_leaderboard(limit=10):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    cur.execute('''
    SELECT winner_name, COUNT(*) as wins
    FROM duel_results
    GROUP BY winner_name
    ORDER BY wins DESC
    LIMIT ?
    ''', (limit,))
    results = cur.fetchall()
    con.close()
    return results


def record_duel_result(winner_name, loser_name):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    cur.execute('INSERT INTO duel_results (winner_name, loser_name) VALUES (?, ?)', (winner_name, loser_name))
    con.commit()
    con.close()

def get_trivia_leaderboard(limit=10):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    cur.execute('''
    SELECT username, MAX(score) as best_score
    FROM trivia_scores
    GROUP BY username
    ORDER BY best_score DESC
    LIMIT ?
    ''', (limit,))

    results = cur.fetchall()
    con.close()

    return results

def update_trivia_score(username, score):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    cur.execute('''
    INSERT OR REPLACE INTO trivia_leaderboard (username, score)
    VALUES (?, COALESCE((SELECT score FROM trivia_leaderboard WHERE username = ?) + ?, ?))
    ''', (username, username, score, score))
    con.commit()
    con.close()



def update_database_schema():
    print("Updating database schema...")
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    # drop_raid_progress_table()

    try:
        # Add last_raid_update column to characters table
        cur.execute('''
        ALTER TABLE characters ADD COLUMN last_raid_update TIMESTAMP;
        ''')
        print("Added last_raid_update column to characters table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("last_raid_update column already exists in characters table.")
        else:
            print(f"Error adding last_raid_update column: {e}")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS raid_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_name TEXT,
            realm TEXT,
            raid_name TEXT,
            lfr_progress INTEGER,
            normal_progress INTEGER,
            heroic_progress INTEGER,
            mythic_progress INTEGER,
            last_updated TEXT,
            UNIQUE(character_name, realm, raid_name)
        )
        ''')
        print("Created raid_progress table.")
    except sqlite3.OperationalError as e:
        print(f"Error creating raid_progress table: {e}")

    try:
        # Create transmog_items table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS transmog_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER UNIQUE,
            name TEXT,
            slot TEXT,
            quality TEXT,
            icon TEXT
        )
        ''')
        print("Created transmog_items table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("transmog_items table already exists.")
        else:
            print(f"Error creating transmog_items table: {e}")

    try:
        # Create transmog_sets table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS transmog_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            head_id INTEGER,
            shoulder_id INTEGER,
            back_id INTEGER,
            chest_id INTEGER,
            wrist_id INTEGER,
            hands_id INTEGER,
            waist_id INTEGER,
            legs_id INTEGER,
            feet_id INTEGER,
            main_hand_id INTEGER,
            off_hand_id INTEGER,
            FOREIGN KEY (head_id) REFERENCES transmog_items(id),
            FOREIGN KEY (shoulder_id) REFERENCES transmog_items(id),
            FOREIGN KEY (back_id) REFERENCES transmog_items(id),
            FOREIGN KEY (chest_id) REFERENCES transmog_items(id),
            FOREIGN KEY (wrist_id) REFERENCES transmog_items(id),
            FOREIGN KEY (hands_id) REFERENCES transmog_items(id),
            FOREIGN KEY (waist_id) REFERENCES transmog_items(id),
            FOREIGN KEY (legs_id) REFERENCES transmog_items(id),
            FOREIGN KEY (feet_id) REFERENCES transmog_items(id),
            FOREIGN KEY (main_hand_id) REFERENCES transmog_items(id),
            FOREIGN KEY (off_hand_id) REFERENCES transmog_items(id)
        );
        ''')
        print("Created transmog_sets table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("transmog_sets table already exists.")
        else:
            print(f"Error creating transmog_sets table: {e}")

    try:
        # Create transmog_votes table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS transmog_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            set_id INTEGER,
            user_id INTEGER,
            vote INTEGER,
            FOREIGN KEY (set_id) REFERENCES transmog_sets(id),
            UNIQUE(set_id, user_id)
        );
        ''')
        print("Created transmog_votes table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("transmog_votes table already exists.")
        else:
            print(f"Error creating transmog_votes table: {e}")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS trivia_leaderboard (
            username TEXT PRIMARY KEY,
            score INTEGER
        )
        ''')
        print("Created trivia_leaderboard table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("trivia_leaderboard table already exists.")
        else:
            print(f"Error creating trivia_leaderboard table: {e}")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS trivia_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created trivia_scores table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("trivia_scores table already exists.")
        else:
            print(f"Error creating trivia_scores table: {e}")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS trivia_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answers TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            difficulty TEXT NOT NULL,
            image_url TEXT
        )
        ''')
        print("Created trivia_questions table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("trivia_questions table already exists.")
        else:
            print(f"Error creating trivia_questions table: {e}")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS character_renders
        (character_name TEXT PRIMARY KEY, render_url TEXT)
        ''')
        print("Created character_renders table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("character_renders table already exists.")
        else:
            print(f"Error creating character_renders table: {e}")

    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS duel_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner_name TEXT,
            loser_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created duel_results table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("duel_results table already exists.")
        else:
            print(f"Error creating duel_results table: {e}")

    con.commit()
    con.close()
    print("Database schema update complete.")