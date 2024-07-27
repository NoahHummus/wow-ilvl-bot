import asyncio
import os
from datetime import datetime

import lightbulb, hikari
import random

from dotenv import load_dotenv

import db, main, chatgptPy
import duel_shit
import raid_shit
import trivia_game
import trivia_shit
import ui_shit
from duel_shit import DuelSelectionMenu
from raid_shit import CURRENT_RAID
from transmog_shit import shorten_url
from trivia_game import TriviaGame

load_dotenv()

token = os.getenv("BOT_TOKEN")
#
# with open('hilariousresponses2023version2real_final.txt', 'r') as file:
#     hilariousresponses = []
#     for line in file:
#         hilariousresponses.append(line)

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
        name=f'Character Name : ilvl (including bagged items)',
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
    return
    # await ctx.respond(random.choice(hilariousresponses))
    
#eulogize a character
@bot.command
@lightbulb.option('name', 'Name of the wow character', str, required=True)
@lightbulb.command('eulogize', 'Generate a euology for a dead character')
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def eulogize(ctx):
    await ctx.respond("Eulogizing....!")
    name = ctx.options.name.lower()
    eulogy = chatgptPy.eulogize(name)
    await ctx.respond("> "+eulogy)
    #await ctx.respond(hikari.Embed(
    #    title="------------------+ RIP +------------------",
    #    colour=0x000000,
    #    ).add_field(
    #    name="-------------------------------------------",
    #    value = eulogy
    #))



@bot.command
@lightbulb.command('raidprogress', 'Show raid progress for all characters')
@lightbulb.implements(lightbulb.SlashCommand)
async def raid_progress(ctx):
    await ctx.respond("Fetching raid progress for all characters...")

    try:
        # Get all raid progress data from the database
        progress_data = db.get_current_raid_progress()

        if not progress_data:
            await ctx.edit_last_response(content="No raid progress data available.")
            return

        participants, non_participants = db.get_raid_participation()

        if not participants and not non_participants:
            await ctx.edit_last_response(content=f"No data available for the current raid: {CURRENT_RAID['name']}")
            return

        embed = hikari.Embed(
            title=f"Raid Progress and Participation - {CURRENT_RAID['name']}",
            color=0x00ff00
        )

        # Participants
        if participants:
            embed.add_field(name="🏆 Raid Participants", value="─────────────────────", inline=False)
            for rank, (character, realm, lfr, normal, heroic, mythic) in enumerate(participants, 1):
                emoji = ui_shit.get_rank_emoji(rank, len(participants))
                progress_bars = (
                    f"LFR: {ui_shit.get_progress_bar(lfr, 9)}\n"
                    f"N: {ui_shit.get_progress_bar(normal, 9)}\n"
                    f"H: {ui_shit.get_progress_bar(heroic, 9)}\n"
                    f"M: {ui_shit.get_progress_bar(mythic, 9)}"
                )
                value = (
                    f"LFR: {lfr}/{9}\n"
                    f"Normal: {normal}/{9}\n"
                    f"Heroic: {heroic}/{9}\n"
                    f"Mythic: {mythic}/{9}\n"
                    f"{progress_bars}"
                )
                embed.add_field(
                    name=f"{emoji} {rank}. {character}-{realm}",
                    value=value,
                    inline=False
                )

        # Non-Participants
        if non_participants:
            embed.add_field(name="💤 Raid Slackers", value="─────────────────────", inline=False)
            slacker_list = []
            for character, realm in non_participants:
                insult = ui_shit.get_insult()
                slacker_list.append(f"🐌 **{character}-{realm}**: {insult}")

            slacker_text = "\n".join(slacker_list)
            # Split into chunks of 1024 characters (Discord's field value limit)
            chunks = [slacker_text[i:i + 1024] for i in range(0, len(slacker_text), 1024)]
            for i, chunk in enumerate(chunks):
                embed.add_field(name="Continued..." if i > 0 else "Slacker Squad", value=chunk, inline=False)

        await ctx.edit_last_response(content="", embed=embed)
    except Exception as e:
        await ctx.edit_last_response(content=f"An error occurred: {str(e)}")


# TODO: Not working, needs to be fixed
# @bot.command
# @lightbulb.option('race', 'Character race (e.g., human, orc, nightelf)', type=str, required=True)
# @lightbulb.option('gender', 'Character gender (male/female)', type=str, required=True)
# @lightbulb.command('transmogroulette', 'Generate a random transmog set')
# @lightbulb.implements(lightbulb.SlashCommand)
# async def transmogroulette(ctx):
#     race = ctx.options.race.lower()
#     gender = ctx.options.gender.lower()
#
#     if gender not in ['male', 'female']:
#         await ctx.respond("Invalid gender. Please use 'male' or 'female'.")
#         return
#
#     transmog_set = db.generate_random_transmog_set()
#
#     embed = hikari.Embed(title="Random Transmog Set", color=0x00ff00)
#
#     wowhead_url = f"https://www.wowhead.com/dressing-room#dz0z0zM89c8"
#     wowhead_url += f"a:{race}"  # Add race
#     wowhead_url += f":{1 if gender == 'female' else 0}"  # Add gender (0 for male, 1 for female)
#
#     item_string = ""
#     for slot, item in transmog_set.items():
#         if item:
#             item_id, name, quality, icon = item
#             embed.add_field(name=slot, value=f"[{name}](https://www.wowhead.com/item={item_id}) (Quality: {quality})")
#             item_string += f"{item_id}:"
#
#     # Add items to the Wowhead URL
#     wowhead_url += f"s:{item_string[:-1]}"  # Remove the last colon
#
#     short_url = shorten_url(wowhead_url)
#     embed.add_field(name="Preview", value=f"[Click here to view in Wowhead Dressing Room]({short_url})", inline=False)
#
#     await ctx.respond(embed=embed)
#     await ctx.respond("React with 👍 to upvote or 👎 to downvote this transmog set!")
#
#
# @bot.listen(hikari.GuildReactionAddEvent)
# async def on_reaction_add(event):
#     if event.emoji_name not in ['👍', '👎']:
#         return
#
#     message = await event.fetch_message()
#     if not message.embeds or 'Set ID:' not in message.embeds[0].footer.text:
#         return
#
#     set_id = int(message.embeds[0].footer.text.split(': ')[1])
#     vote = 1 if event.emoji_name == '👍' else -1
#
#     db.vote_transmog(set_id, event.user_id, vote)
#
#
# @bot.command
# @lightbulb.option('set_id', 'The ID of the transmog set', type=int)
# @lightbulb.command('transmogvotes', 'Get votes for a transmog set')
# @lightbulb.implements(lightbulb.SlashCommand)
# async def transmogvotes(ctx):
#     set_id = ctx.options.set_id
#     votes = db.get_transmog_votes(set_id)
#
#     embed = hikari.Embed(title=f"Votes for Transmog Set {set_id}", color=0x00ff00)
#     embed.add_field(name="Upvotes", value=str(votes['upvotes']))
#     embed.add_field(name="Downvotes", value=str(votes['downvotes']))
#
#     await ctx.respond(embed=embed)


@bot.command
@lightbulb.option('num_questions', 'Number of questions to ask', int, min_value=1, max_value=20, default=5)
@lightbulb.command('wow_trivia', 'Start a World of Warcraft trivia game')
@lightbulb.implements(lightbulb.SlashCommand)
async def wow_trivia(ctx):
    # Send an initial response
    await ctx.respond("Preparing the WoW Trivia game...")

    num_questions = ctx.options.num_questions
    questions = trivia_shit.get_all_trivia_questions()

    if not questions:
        await ctx.edit_last_response("No questions available. Please try again later.")
        return

    game = TriviaGame(ctx, questions, num_questions)
    try:
        if await game.setup_game():
            final_scores = await game.play()

            # Display final scores with a visual representation
            embed = hikari.Embed(title="Trivia Game Over!", color=0x00ff00)
            embed.set_thumbnail("img/orc presentation.png")

            max_score = max(player['score'] for player in final_scores) if final_scores else 0
            for player in final_scores:
                score_bar = "█" * int(player['score'] * 10 / max_score) + "░" * (10 - int(player['score'] * 10 / max_score))
                embed.add_field(name=player['name'], value=f"Score: {player['score']} {score_bar}", inline=False)

            await ctx.edit_last_response(embed=embed, content=None)

            # Save scores to database
            for player in final_scores:
                db.save_trivia_score(player['name'], player['score'])
    except Exception as e:
        await ctx.edit_last_response(f"An error occurred during the trivia game: {str(e)}")

@bot.command
@lightbulb.command('trivia_leaderboard', 'Display the WoW Trivia leaderboard')
@lightbulb.implements(lightbulb.SlashCommand)
async def trivia_leaderboard(ctx):
    await trivia_game.display_leaderboard(ctx)


@bot.command
@lightbulb.option('difficulty', 'Difficulty of the question (Easy, Medium, Hard)', str, required=True)
@lightbulb.option('correct_answer', 'The correct answer', str, required=True)
@lightbulb.option('wrong_answer3', 'Third wrong answer', str, required=True)
@lightbulb.option('wrong_answer2', 'Second wrong answer', str, required=True)
@lightbulb.option('wrong_answer1', 'First wrong answer', str, required=True)
@lightbulb.option('question', 'The trivia question', str, required=True)
@lightbulb.command('add_trivia', 'Add a new trivia question')
@lightbulb.implements(lightbulb.SlashCommand)
async def add_trivia(ctx):
    question = ctx.options.question
    answers = [ctx.options.correct_answer, ctx.options.wrong_answer1, ctx.options.wrong_answer2,
               ctx.options.wrong_answer3]
    correct_index = 0  # The correct answer is always the first one
    difficulty = ctx.options.difficulty.capitalize()

    if difficulty not in ['Easy', 'Medium', 'Hard']:
        await ctx.respond("Invalid difficulty. Please choose Easy, Medium, or Hard.")
        return

    # Shuffle the answers
    random.shuffle(answers)
    correct_index = answers.index(ctx.options.correct_answer)

    success = db.add_trivia_question(question, answers, correct_index, difficulty)

    if success:
        await ctx.respond("Your trivia question has been added successfully!")
    else:
        await ctx.respond("There was an error adding your question. Please try again later.")


@bot.command
@lightbulb.command("duel", "Initiate a duel between two characters")
@lightbulb.implements(lightbulb.SlashCommand)
async def duel(ctx: lightbulb.Context) -> None:
    characters = db.get_registered_characters()

    if len(characters) < 2:
        await ctx.respond("Not enough characters registered for a duel.")
        return

    first_character = await select_character(ctx, characters, "first")
    if first_character:
        remaining_characters = [c for c in characters if c != first_character]
        second_character = await select_character(ctx, remaining_characters, "second")
        if second_character:
            await ctx.edit_last_response(
                f"Duel initiated between {first_character['name']} and {second_character['name']}! Generating duel narrative...",
                components=[]
            )
            await duel_shit.initiate_duel(ctx, first_character, second_character)


async def select_character(ctx: lightbulb.Context, characters, ordinal):
    buttons = (
        ctx.bot.rest.build_action_row()
        .add_button(hikari.ButtonStyle.PRIMARY, "prev")
        .set_label("Previous")
        .add_to_container()
        .add_button(hikari.ButtonStyle.SUCCESS, "select")
        .set_label("Select")
        .add_to_container()
        .add_button(hikari.ButtonStyle.PRIMARY, "next")
        .set_label("Next")
        .add_to_container()
    )

    current_index = 0

    async def create_embed(character):
        embed = hikari.Embed(
            title=f"Select the {ordinal} character for the duel",
            description=f"**{character['name']}** ({character['realm']})",
            color=hikari.Color(0x00ff00)
        )
        render_url = db.get_character_render(character['name'])
        if render_url:
            embed.set_image(render_url)
        return embed

    initial_embed = await create_embed(characters[current_index])
    response = await ctx.respond(embed=initial_embed, components=[buttons])
    message = await response.message()

    while True:
        try:
            event = await ctx.bot.wait_for(
                hikari.InteractionCreateEvent,
                timeout=60.0,
                predicate=lambda e: isinstance(e.interaction, hikari.ComponentInteraction)
                                    and e.interaction.user.id == ctx.author.id
                                    and e.interaction.message.id == message.id
            )

            if event.interaction.custom_id == "prev":
                current_index = (current_index - 1) % len(characters)
            elif event.interaction.custom_id == "next":
                current_index = (current_index + 1) % len(characters)
            elif event.interaction.custom_id == "select":
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    content=f"You selected {characters[current_index]['name']}!",
                    embed=None,
                    components=[]
                )
                return characters[current_index]

            new_embed = await create_embed(characters[current_index])
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE,
                embed=new_embed,
                components=[buttons]
            )

        except asyncio.TimeoutError:
            await ctx.edit_last_response("Character selection timed out. Please try again.", components=[])
            return None


@bot.command
@lightbulb.command('duel_leaderboard', 'Show the duel leaderboard')
@lightbulb.implements(lightbulb.SlashCommand)
async def duel_leaderboard(ctx):
    leaderboard = db.get_duel_leaderboard(limit=10)  # Get top 10 duelists

    if not leaderboard:
        await ctx.respond("No duels have been recorded yet. Be the first to make your mark in the arena!")
        return

    top_duelist = leaderboard[0][0]  # Name of the top duelist
    top_duelist_render = db.get_character_render(top_duelist)

    embed = hikari.Embed(
        title="🏆 Duel Leaderboard 🏆",
        description="Top duelists and their glorious victories!",
        color=hikari.Color(0xFFD700)  # Gold color
    )

    # Add a fancy header only if there are entries
    if leaderboard:
        embed.add_field(
            name="═════════ Rankings ═════════",
            value="\u200b",  # Zero-width space to avoid empty string error
            inline=False
        )

    for rank, (name, wins) in enumerate(leaderboard, start=1):
        if rank == 1:
            emoji = "👑"
            name = f"**{name}**"
        elif rank == 2:
            emoji = "🥈"
        elif rank == 3:
            emoji = "🥉"
        elif rank <= 5:
            emoji = "🏅"
        else:
            emoji = "🔹"

        # Add some flavor text based on win count
        if wins > 50:
            title = "Legendary Duelist"
        elif wins > 30:
            title = "Master Duelist"
        elif wins > 15:
            title = "Expert Duelist"
        elif wins > 5:
            title = "Skilled Duelist"
        else:
            title = "Aspiring Duelist"

        embed.add_field(
            name=f"{emoji} Rank #{rank}: {name}",
            value=f"⚔️ {wins} wins • 🎖️ {title}",
            inline=False
        )

    # Add a footer with the current date
    current_date = datetime.now().strftime("%B %d, %Y")
    embed.set_footer(text=f"Leaderboard updated on {current_date}")

    # Set the thumbnail to the top duelist's character render
    if top_duelist_render:
        embed.set_thumbnail(top_duelist_render)
    else:
        # Fallback to a default image if no render is available
        embed.set_thumbnail("https://example.com/path/to/default_duel_icon.png")

    await ctx.respond(embed=embed)

@bot.listen(hikari.StartingEvent)
async def on_starting(event):
    print("Bot is starting...")
    db.update_database_schema()  # Update the database schema before the bot fully starts
    await raid_shit.update_all_raid_progress()
    # main.populate_transmog_items()  # This might take a while and only needs to be done once


bot.run()