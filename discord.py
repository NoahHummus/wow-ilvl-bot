import lightbulb
import hikari
import requests
import db
import main

with open('token.txt', 'r') as file:
    token = file.read()
print(token)

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
    ilvllist = main.get_ilvl_from_profile(main.threaded_get_all_characters())
    await ctx.respond(hikari.Embed(
        title=f'-----------------+ BIGGEST BOYS +-----------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Equipped ilvl',
        value = main.build_ranking(ilvllist)
    ))

#check M+ rating
@bot.command
@lightbulb.command('mythic', 'Get a Mythic+ ranking from the list of registered characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def mythic(ctx):
    await ctx.respond("Retrieving....!")
    mythiclist = main.get_mythic_from_profile(main.threaded_get_all_mythics())
    await ctx.respond(hikari.Embed(
        title=f'------------+ SWEATIEST TRYHARDS +------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Mythic+ rating',
        value = main.build_ranking_mythic(mythiclist)
    ))

#change ownership of character
@bot.command
@lightbulb.option('name', 'Name of the wow character', str, required=True)
@lightbulb.option('owner', 'Who this character should be registered to', str, required=True)
@lightbulb.command('changeowner', 'Reassign a character to the correct owner')
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def changeowner(ctx: lightbulb.Context) -> None:
    name = ctx.options.name.lower()
    try:
        owner_id = int(ctx.options.owner[2:-1])
        owner = ctx.get_guild().get_member(owner_id)
    except:
        owner = None
    print(f"character name: {name}")
    print(f"new owner: {owner}")
    await ctx.respond(db.change_owner(name, owner))
    
#single character ownership checker
#@bot.command
#@lightbulb.option('name', 'Name of the wow character', str, required=True)
#@lightbulb.command('whoowns', 'Check the registered owner of a character')
#@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
#async def whoowns(ctx: lightbulb.Context) -> None:
#    name = ctx.options.name.lower()
#    print(f"character name: {name}")
#    await ctx.respond(db.check_owner(name))
    
#check ownership of all characters
@bot.command
@lightbulb.command('whoowns', 'Check the registered owners of all characters')
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def whoowns2(ctx: lightbulb.Context) -> None:
    await ctx.respond(hikari.Embed(
        title=f'-----------------+ OWNERS +-----------------',
        colour=0x3B9DFF,
        ).add_field(
        name=f'Character Name : Registered Owner',
        value = main.list_owners()
    ))

bot.run()
