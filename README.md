# wow-ilvl-bot

Create a file called ".env". Set these values:
CLIENT_SECRET="xyz" (For wow api)
CLIENT_ID="GGEZ" (wow api)
BOT_TOKEN="XYZ" (discord developer bot token)
GROQ_API_KEY="daf" (get apikey at groqcloud)

This is shid.

Discord -> main -> db

Discord.py is what listens for the slash commands and calls main. Main does the REST stuff, and calls the db functions that talks with the local db.

Additional info:

chatgptPy.py is now used. It only creates eulogies currently. You need to provide your own API key for that, I ain't sharin'

update.py is run in a separate instance and automatically updates ilvl and mythic progression at weekly reset (coded in EST, so it goes at 10:01, feel free to update to reflect your time zone)

Oh also, you should have a file named "hilariousresponses2023version2real_final.txt" that has one response to the /iswowdead prompt per line
