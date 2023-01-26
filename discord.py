import lightbulb, hikari
import requests
import random
import schedule, time, threading
import db, main


with open('token.txt', 'r') as file:
    token = file.read()
print(token)

with open('hilariousresponses2023version2real_final.txt', 'r') as file:
    hilariousresponses = []
    for line in file:
        hilariousresponses.append(line)

#weekly db update for progging
def update_prog_log():
    print("updating prog log, in discord")
    db.update_prog_log();
def run_threaded_job(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
schedule.every().tuesday.at("10:01").do(run_threaded_job, update_prog_log)

bot = lightbulb.BotApp(token=token, intents=hikari.Intents.ALL, default_enabled_guilds=(97389122452193280, 428374533154668544))

#register character
@bot.command
@lightbulb.option('name', 'Name of the wow character', str, required=True)
@lightbulb.option('realm', 'Realm for the character', str, default='kul-tiras')
@lightbulb.command('register', 'Register your wow character')
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def register(ctx: lightbulb.Context) -> None:
    user = ctx.author
    name = ctx.options.name.lower()
    realm = ctx.options.realm.lower()
    print(f"character name: {name}")
    print(f"registered realm : {realm}")
    await ctx.respond(db.register_character(user, name, realm))

#check ilvls
@bot.command
@lightbulb.command('ilvl', 'Get an ilvl ranking from the list of registered characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def ilvl(ctx):
    await ctx.respond("Retrieving....!")
    ilvllist = main.get_ilvl_from_profile(main.get_all())
    await ctx.respond(hikari.Embed(
        title=f'-----------------+ BIGGEST BOYS +-----------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Equipped ilvl',
        value = main.build_ranking(ilvllist, 'ilvl')
    ))

#check M+ rating
@bot.command
@lightbulb.command('mythic', 'Get a Mythic+ ranking from the list of registered characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def mythic(ctx):
    await ctx.respond("Retrieving....!")
    mythiclist = main.get_mythic_from_profile(main.get_all('/mythic-keystone-profile'))
    await ctx.respond(hikari.Embed(
        title=f'------------+ SWEATIEST TRYHARDS +------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Mythic+ rating',
        value = main.build_ranking(mythiclist, 'mythic')
    ))
    
#check M+ progress since last weekly update
@bot.command
@lightbulb.command('mythicprog', 'Get a Mythic+ rating progression ranking from the list of registered characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def mythicprog(ctx):
    await ctx.respond("Retrieving....!")
    proglist = main.get_mythicprog_from_profile(main.get_all('/mythic-keystone-profile'))
    await ctx.respond(hikari.Embed(
        title=f'---------------+ PROGGERS AF +---------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Mythic+ progression since reset',
        value = main.build_ranking(proglist, 'prog')
    ))    

#check ilvl progress since last weekly update
@bot.command
@lightbulb.command('ilvlprog', 'Get an ilvl progression ranking from the list of registered characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def mythicprog(ctx):
    await ctx.respond("Retrieving....!")
    proglist = main.get_ilvlprog_from_profile(main.get_all())
    await ctx.respond(hikari.Embed(
        title=f'---------------+ PROGGERS AF +---------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : ilvl progression since reset',
        value = main.build_ranking(proglist, 'prog')
    ))

#check number of set pieces
@bot.command
@lightbulb.command('sets', 'Get a list of how many set pieces each character has equipped')
@lightbulb.implements(lightbulb.SlashCommand)
async def sets(ctx):
    await ctx.respond("Retrieving....!")
    piecelist = main.get_setpieces_from_profile(main.get_all('/equipment'))
    await ctx.respond(hikari.Embed(
        title=f"-------------+ WHO'S BRICKED UP? +-------------",
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Equipped tier pieces',
        value = main.build_ranking(piecelist, 'pieces')
    ))
    
#ask the bot if wow is up
@bot.command
@lightbulb.command('iswowup', 'Ask the bot if WoW is up right now')
@lightbulb.implements(lightbulb.SlashCommand)
async def iswowup(ctx: lightbulb.Context) -> None:
    if main.isWowDown():
        f = hikari.File('img/spongebob.png')
        await ctx.respond(f)
    else:
        await ctx.respond('WoW servers are up, so why are you here talking to a bot and not progging?')
        
#ask the bot if wow is down
@bot.command
@lightbulb.command('iswowdown', 'Ask the bot if WoW is down right now')
@lightbulb.implements(lightbulb.SlashCommand)
async def iswowdown(ctx: lightbulb.Context) -> None:
    if main.isWowDown():
        f = hikari.File('img/spongebob2.png')
        await ctx.respond(f)
    else:
        await ctx.respond('WoW servers are up, so why are you here talking to a bot and not progging?')

#ask the bot if wow is dead
@bot.command
@lightbulb.command('iswowdead', 'Ask the bot if WoW is dead')
@lightbulb.implements(lightbulb.SlashCommand)
async def iswowdead(ctx: lightbulb.Context) -> None:
    await ctx.respond(random.choice(hilariousresponses))

bot.run()