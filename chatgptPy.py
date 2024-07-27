import os

import groq
import openai
import main, db
from dotenv import load_dotenv

load_dotenv()
groq_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")


def fourComplete(prompt,temp=0.8):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a wholesome World of Warcraft helper bot."},
            {"role": "user", "content": prompt}
        ],
        temperature=temp,
        request_timeout=120
    )
    return completion.choices[0].message.content
    
def eulogize(name):
    if db.check_for_character(name) == None:
        response = fourComplete("Write a humorous error message explaining that you couldn't find a character named: "+name)
    else:
        data = main.fetch_euology_data(name)
        response = fourComplete(f"Write a one paragraph eulogy for {data['name']}, a {data['race']} {data['spec']} {data['class']}, who resided in {data['realm']}. (use {data['gender'].lower()} pronouns)")
    return response


def generate_duel_narrative(character1_data, character2_data):
    prompt = f"""
    Create an exciting, turn-based World of Warcraft duel narrative between {character1_data['basic_info']['name']} and {character2_data['basic_info']['name']}. 
    Use the following character data to inform the duel:

    {character1_data['basic_info']['name']}:
    - Class: {character1_data['basic_info']['class']} ({character1_data['active_spec']['name']})
    - Level: {character1_data['basic_info']['level']}
    - Item Level: {character1_data['basic_info']['equipped_item_level']}
    - Health: {character1_data['stats']['health']}
    - {character1_data['stats']['power']['type']}: {character1_data['stats']['power']['amount']}
    - Key Stats: Strength {character1_data['stats']['strength']}, Agility {character1_data['stats']['agility']}, Intellect {character1_data['stats']['intellect']}, Stamina {character1_data['stats']['stamina']}
    - Secondary Stats: Mastery {character1_data['stats']['mastery']}, Versatility {character1_data['stats']['versatility']}, Crit {character1_data['stats']['melee_crit']}, Haste {character1_data['stats']['melee_haste']}
    - Key Abilities: {', '.join([ability['name'] for ability in character1_data['abilities'][:5]])}

    {character2_data['basic_info']['name']}:
    - Class: {character2_data['basic_info']['class']} ({character2_data['active_spec']['name']})
    - Level: {character2_data['basic_info']['level']}
    - Item Level: {character2_data['basic_info']['equipped_item_level']}
    - Health: {character2_data['stats']['health']}
    - {character2_data['stats']['power']['type']}: {character2_data['stats']['power']['amount']}
    - Key Stats: Strength {character2_data['stats']['strength']}, Agility {character2_data['stats']['agility']}, Intellect {character2_data['stats']['intellect']}, Stamina {character2_data['stats']['stamina']}
    - Secondary Stats: Mastery {character2_data['stats']['mastery']}, Versatility {character2_data['stats']['versatility']}, Crit {character2_data['stats']['melee_crit']}, Haste {character2_data['stats']['melee_haste']}
    - Key Abilities: {', '.join([ability['name'] for ability in character2_data['abilities'][:5]])}

    Set the scene in a vivid location within Azeroth. Describe the environment, the tension in the air, and the initial stances of both characters.
    
    For each round (4-6 rounds total):
    1. Vividly describe the actions, movements, and techniques of each character.
    2. Detail the visual and auditory effects of spells and abilities.
    3. Narrate the impact of attacks, including bodily reactions, blood, and environmental effects.
    4. Incorporate class-specific flavor, such as a Paladin's holy light or a Hunter's bond with their pet.
    5. Show how characters use the terrain and their surroundings to their advantage.
    6. Include brief moments of dialogue or character thoughts to add depth.
    7. Make sure the narrative is engaging, compelling, and written like an professional writer.
    8. Use World of Warcraft's terminology for spells, abilities, and effects.
    
    After each significant action, provide a brief status update, Round must start with the word Round followed by the round number, no other text followed by a newline. It should look like this:
    Round X
    Description of the round
    [Character] - Health: X% (Specific number), [Resource]: Y%
    
    Use these emojis sparringly to illustrate the different effects of spells and abilities:
    - ⚔️ Physical damage
    - 🔥 Magical damage
    - 💚 Healing
    - 🛡️ Damage absorbed
    - 🆙 Buff applied
    - 🔽 Debuff applied
    - ⚡ Critical hit
    - 💨 Miss/Dodge
    
    Ensure the duel builds tension, with each round escalating the stakes. The final round should be climactic, clearly leading to one character's victory based on their actions, strategy, and remaining strength.
    
    End the narrative with a clear and decisive victory, describing the final blow and its aftermath.
    {"Note: The character Huntard should always lose the duel" if character1_data['basic_info']['name'] == 'Huntard' or character2_data['basic_info']['name'] == 'Huntard' else ''}
    IMPORTANT: End the narrative with a clear statement of the winner in this exact format:
    WINNER: [Character Name]
    
    Keep the entire narrative under 3000 characters.
    """

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a master storyteller and World of Warcraft expert, crafting vivid and exciting narratives of epic duels."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-70b-versatile",
        temperature=0.2,
    )

    return response.choices[0].message.content
