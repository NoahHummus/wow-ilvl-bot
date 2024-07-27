import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, Any

import requests

import db
import main
from main import get_character_profile

# Define the current raid
CURRENT_RAID = {
    "name": "Amirdrassil, the Dream's Hope",
    "id": 1207,
    "bosses": [
        "Kazzara, the Hellforged",
        "The Amalgamation Chamber",
        "The Forgotten Experiments",
        "Assault of the Zaqali",
        "Rashok, the Elder",
        "The Vigilant Steward, Zskarn",
        "Magmorax",
        "Echo of Neltharion",
        "Scalecommander Sarkareth"
    ]
}

def parse_raid_progress(data):
    if not data and 'encounters' in data.keys() and 'expansions' not in data.keys():
        return None

    # Get the latest expansion's raid data
    latest_expansion = data['expansions'][-1]
    latest_raids = latest_expansion['instances']

    # Find the most recent raid

    progress_list = []
    for raid in latest_raids:
        progress = {
            'name': raid['instance']['name'],
            'lfr_progress': 0,
            'normal_progress': 0,
            'heroic_progress': 0,
            'mythic_progress': 0,
        }

        for mode in raid['modes']:
            if mode['difficulty']['type'] == 'LFR':
                progress['lfr_progress'] = mode['progress']['completed_count']
            if mode['difficulty']['type'] == 'NORMAL':
                progress['normal_progress'] = mode['progress']['completed_count']
            elif mode['difficulty']['type'] == 'HEROIC':
                progress['heroic_progress'] = mode['progress']['completed_count']
            elif mode['difficulty']['type'] == 'MYTHIC':
                progress['mythic_progress'] = mode['progress']['completed_count']
        progress_list.append(progress)

    return progress_list


def update_character_raid_progress(character_name, realm, progress_data):
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()

    # Assuming you have a raid_progress table
    cur.execute('''
    INSERT OR REPLACE INTO raid_progress 
    (character_name, realm, raid_name, lfr_progress, normal_progress, heroic_progress, mythic_progress, last_updated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (character_name, realm, progress_data['name'], progress_data['lfr_progress'],
          progress_data['normal_progress'], progress_data['heroic_progress'],
          progress_data['mythic_progress'], progress_data['last_updated']))

    con.commit()
    con.close()


async def update_all_raid_progress(force=False):
    print("Updating raid progress for all characters...")
    if force:
        characters = db.get_all_registered_characters()
    else:
        characters = db.get_raid_characters_to_update()

    if not characters:
        print("All characters are up to date. No updates needed.")
        return

    updated_count = 0
    for character_name, realm in characters:
        try:
            data = await main.get_character_raid_profile(realm, character_name)
            if data and data['encounters']:
                progress_list = parse_raid_progress(data['encounters'])
                for progress in progress_list:
                    if progress:
                        updated_count += 1
                        progress['last_updated'] = datetime.now().isoformat()
                        update_character_raid_progress(character_name, realm, progress)
                        print(f"Updated raid progress for {character_name}-{realm}")
                    else:
                        print(f"No raid progress data available for {character_name}-{realm}")
            else:
                print(f"Failed to fetch data for {character_name}-{realm}")

            # Add a small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error updating raid progress for {character_name}-{realm}: {str(e)}")

    print(f"Raid progress update complete. Updated {updated_count} characters.")
