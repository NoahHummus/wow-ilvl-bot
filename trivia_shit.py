import json
import random
import sqlite3
import uuid
from functools import lru_cache

import db
import main


def generate_character_trivia(character_data):
    questions = []

    try:
        # Basic character info questions
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What level is the character {character_data['name']}?",
            "answers": [str(character_data['level'] - 5), str(character_data['level']),
                        str(character_data['level'] + 5), str(character_data['level'] + 10)],
            "correct_index": 1,
            "difficulty": "Easy"
        })
    except KeyError:
        print(f"Error creating level question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What class is the character {character_data['name']}?",
            "answers": [character_data['character_class']['name'], "Warrior", "Mage", "Rogue"],
            "correct_index": 0,
            "difficulty": "Easy"
        })
    except KeyError:
        print(f"Error creating class question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What race is the character {character_data['name']}?",
            "answers": [character_data['race']['name'], "Human", "Orc", "Night Elf"],
            "correct_index": 0,
            "difficulty": "Easy"
        })
    except KeyError:
        print(f"Error creating race question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What faction does {character_data['name']} belong to?",
            "answers": ["Alliance", "Horde", "Neutral", "Mercenary"],
            "correct_index": 1 if character_data['faction']['type'] == 'HORDE' else 0,
            "difficulty": "Easy"
        })
    except KeyError:
        print(f"Error creating faction question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What is {character_data['name']}'s active specialization?",
            "answers": [character_data['active_spec']['name'], "Protection", "Restoration", "Arcane"],
            "correct_index": 0,
            "difficulty": "Medium"
        })
    except KeyError:
        print(f"Error creating specialization question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What realm does {character_data['name']} play on?",
            "answers": [character_data['realm']['name'], "Stormrage", "Illidan", "Area 52"],
            "correct_index": 0,
            "difficulty": "Medium"
        })
    except KeyError:
        print(f"Error creating realm question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"How many achievement points does {character_data['name']} have?",
            "answers": [str(character_data['achievement_points'] - 500), str(character_data['achievement_points']),
                        str(character_data['achievement_points'] + 500),
                        str(character_data['achievement_points'] + 1000)],
            "correct_index": 1,
            "difficulty": "Hard"
        })
    except KeyError:
        print(f"Error creating achievement points question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What is {character_data['name']}'s average item level?",
            "answers": [str(character_data['average_item_level'] - 10), str(character_data['average_item_level']),
                        str(character_data['average_item_level'] + 10), str(character_data['average_item_level'] + 20)],
            "correct_index": 1,
            "difficulty": "Medium"
        })
    except KeyError:
        print(f"Error creating item level question for {character_data.get('name', 'Unknown character')}")

    try:
        questions.append({
            "id": str(uuid.uuid4()),
            "question": f"What is {character_data['name']}'s equipped item level?",
            "answers": [str(character_data['equipped_item_level'] - 10), str(character_data['equipped_item_level']),
                        str(character_data['equipped_item_level'] + 10),
                        str(character_data['equipped_item_level'] + 20)],
            "correct_index": 1,
            "difficulty": "Medium"
        })
    except KeyError:
        print(f"Error creating equipped item level question for {character_data.get('name', 'Unknown character')}")

    if 'guild' in character_data:
        try:
            questions.append({
                "id": str(uuid.uuid4()),
                "question": f"What guild does {character_data['name']} belong to?",
                "answers": [character_data['guild']['name'], "Method", "Limit", "Pieces"],
                "correct_index": 0,
                "difficulty": "Hard"
            })
        except KeyError:
            print(f"Error creating guild question for {character_data.get('name', 'Unknown character')}")

    if 'covenant_progress' in character_data and 'chosen_covenant' in character_data['covenant_progress']:
        try:
            questions.append({
                "id": str(uuid.uuid4()),
                "question": f"Which covenant did {character_data['name']} choose?",
                "answers": [character_data['covenant_progress']['chosen_covenant']['name'], "Kyrian", "Venthyr",
                            "Night Fae"],
                "correct_index": 0,
                "difficulty": "Medium"
            })
        except KeyError:
            print(f"Error creating covenant question for {character_data.get('name', 'Unknown character')}")

        try:
            questions.append({
                "id": str(uuid.uuid4()),
                "question": f"What is {character_data['name']}'s renown level with their covenant?",
                "answers": [str(character_data['covenant_progress']['renown_level'] - 5),
                            str(character_data['covenant_progress']['renown_level']),
                            str(character_data['covenant_progress']['renown_level'] + 5),
                            str(character_data['covenant_progress']['renown_level'] + 10)],
                "correct_index": 1,
                "difficulty": "Hard"
            })
        except KeyError:
            print(f"Error creating renown level question for {character_data.get('name', 'Unknown character')}")

    return questions


def update_character_data():
    characters = db.get_all_registered_characters()
    all_questions = []

    for character_name, realm in characters:
        character_data = main.get_all_character_data(realm, character_name)
        if character_data:
            questions = generate_character_trivia(character_data)
            all_questions.extend(questions)

    return all_questions


def get_character_trivia(num_questions=5):
    all_questions = update_character_data()
    return random.sample(all_questions, min(num_questions, len(all_questions)))


@lru_cache(maxsize=1)
def get_all_trivia_questions():
    # Load static questions
    all_questions = load_static_questions()

    # Get character-specific questions
    characters = db.get_all_registered_characters()

    for character_name, realm in characters:
        character_data = main.get_all_character_data(realm, character_name)
        if character_data:
            questions = generate_character_trivia(character_data)
            all_questions.extend(questions)

    # Get user-added questions from the database
    con = sqlite3.connect('wowdb.db')
    cur = con.cursor()
    cur.execute('SELECT question, answers, correct_index, difficulty, image_url FROM trivia_questions')
    user_questions = cur.fetchall()
    con.close()

    for q in user_questions:
        all_questions.append({
            "question": q[0],
            "answers": json.loads(q[1]),
            "correct_index": q[2],
            "difficulty": q[3],
            "image_url": q[4]
        })

    return all_questions

    return all_questions


def load_static_questions():
    with open('trivia_questions.json', 'r') as file:
        questions = json.load(file)

    # Add unique identifier to each question
    for question in questions:
        question['id'] = str(uuid.uuid4())

    return questions