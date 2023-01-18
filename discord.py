import lightbulb
import hikari
import requests
import db
import main


with open('token.txt', 'r') as file:
    token = file.read()

print(token)

bot = lightbulb.BotApp(token=token, default_enabled_guilds=(966169335431303198, 97389122452193280))




@bot.command
@lightbulb.option('name', 'Name of the wow character', str, required=True)
@lightbulb.option('realm', 'Realm for the character', str, default='kul-tiras')
@lightbulb.command('register', 'Register your wow character')
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def register(ctx: lightbulb.Context) -> None:
    user = ctx.author
    name = ctx.options.name.lower()
    realm = ctx.options.realm.lower()
    print(f"registered realm : {realm}")
    await ctx.respond(db.register_character(user, name, realm))




@bot.command
@lightbulb.command('ilvl', 'Get an ilvl ranking from the list of registered characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def ilvl(ctx):
    await ctx.respond("Retrieving....!")
    ilvllist = main.get_ilvl_from_profile(main.get_all_characters())
    await ctx.respond(hikari.Embed(
title=f'----------------------+ BIGGEST BOYS +----------------------',
colour=0x3B9DFF,
)
.add_field(
name=f'Character Name : Equipped ilvl',
value = main.build_ranking(ilvllist)
))



#if __name__ == "__main__":
    #main.get_all_characters()w

bot.run()
