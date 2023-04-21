import openai
import main,db

with open('secret.env', 'r') as file:
    openai.api_key = file.read()
print(openai.api_key)

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