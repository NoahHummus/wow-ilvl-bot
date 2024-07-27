# trivia_game.py

import random
import asyncio
import hikari
import db
import ui_shit
from ui_shit import get_rank_emoji

# Custom emojis for difficulty levels (replace these IDs with your actual emoji IDs)
DIFFICULTY_EMOJIS = {
    "Easy": "<:easy:298568401486479410>",
    "Medium": "<:medium:1253177425135669248>",
    "Hard": "<:hard:765730781624401920>"
}


class TriviaGame:
    def __init__(self, ctx, questions, num_questions):
        self.ctx = ctx
        self.questions = random.sample(questions, min(num_questions, len(questions)))
        self.players = {}
        self.current_question = 0
        self.num_questions = num_questions

    async def setup_game(self):
        embed = hikari.Embed(title="WoW Trivia Game", description="Click the button below to join the game!",
                             color=0x00ff00)
        # embed.set_thumbnail("img/orc presentation.png")  # Replace with an actual WoW trivia logo
        join_button = self.ctx.bot.rest.build_action_row().add_button(hikari.ButtonStyle.PRIMARY,
                                                                      "join_game").set_label(
            "Join Game").add_to_container()
        start_button = self.ctx.bot.rest.build_action_row().add_button(hikari.ButtonStyle.SUCCESS,
                                                                       "start_game").set_label(
            "Start Game").add_to_container()

        await self.ctx.edit_last_response(embed=embed, components=[join_button, start_button])

        try:
            while True:
                try:
                    event = await self.ctx.bot.wait_for(hikari.InteractionCreateEvent, timeout=6969.0)
                    if event.interaction.custom_id == "join_game":
                        user = event.interaction.user
                        if user.id not in self.players:
                            self.players[user.id] = {"name": user.username, "score": 0}
                            await event.interaction.create_initial_response(
                                hikari.ResponseType.MESSAGE_UPDATE,
                                embed=self.get_player_list_embed()
                            )
                    elif event.interaction.custom_id == "start_game":
                        if event.interaction.user.id == self.ctx.author.id:
                            if len(self.players) > 0:
                                await event.interaction.create_initial_response(
                                    hikari.ResponseType.MESSAGE_UPDATE,
                                    content="Game starting!", embed=None, components=[]
                                )
                                return True
                            else:
                                await event.interaction.create_initial_response(
                                    hikari.ResponseType.MESSAGE_UPDATE,
                                    content="Cannot start the game without players!",
                                    embed=self.get_player_list_embed()
                                )
                except asyncio.TimeoutError:
                    await self.ctx.edit_last_response("Game setup timed out. Please start a new game.", components=[])
                    return False
        except Exception as e:
            await self.ctx.edit_last_response(f"An error occurred during game setup: {str(e)}")
            return False
    def get_player_list_embed(self):
        embed = hikari.Embed(title="WoW Trivia Game", description="Current players:", color=0x00ff00)
        embed.set_thumbnail("img/orc presentation.png")  # Replace with an actual WoW trivia logo
        for player in self.players.values():
            embed.add_field(name=player['name'], value="Ready to play!", inline=False)
        return embed

    async def play(self):
        for question in self.questions:
            await self.ask_question(question)
            self.current_question += 1

        return self.get_final_scores()

    async def ask_question(self, question):
        embed = hikari.Embed(title=f"Question {self.current_question + 1}", description=question['question'],
                             color=0x00ff00)
        embed.set_footer(text=f"Difficulty: {DIFFICULTY_EMOJIS[question['difficulty']]} {question['difficulty']}")

        progress = self.current_question / self.num_questions
        progress_bar = ui_shit.get_progress_bar(self.current_question, self.num_questions)
        embed.add_field(name="Progress", value=f"{progress_bar} {self.current_question}/{self.num_questions}",
                        inline=False)

        buttons = self.ctx.bot.rest.build_action_row()
        for i, answer in enumerate(question['answers']):
            buttons.add_button(hikari.ButtonStyle.SECONDARY, f"answer_{i}").set_label(answer).add_to_container()

        message = await self.ctx.respond(embed=embed, components=[buttons])

        answered_players = set()
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < 15.0 and len(answered_players) < len(self.players):
            try:
                event = await self.ctx.bot.wait_for(hikari.InteractionCreateEvent,
                                                    timeout=15.0 - (asyncio.get_event_loop().time() - start_time))
                if event.interaction.user.id in self.players and event.interaction.user.id not in answered_players:
                    answered_players.add(event.interaction.user.id)
                    selected_answer = int(event.interaction.custom_id.split('_')[1])
                    if selected_answer == question['correct_index']:
                        points = self.calculate_points(question['difficulty'])
                        self.players[event.interaction.user.id]['score'] += points
                        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,
                                                                        content=f"✅ Correct! You earned {points} points.",
                                                                        flags=hikari.MessageFlag.EPHEMERAL)
                    else:
                        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE,
                                                                        content="❌ Wrong answer!",
                                                                        flags=hikari.MessageFlag.EPHEMERAL)
            except asyncio.TimeoutError:
                break

        correct_answer = question['answers'][question['correct_index']]
        await message.edit(f"Time's up! The correct answer was: {correct_answer}", components=[])

    def calculate_points(self, difficulty):
        return {"Easy": 1, "Medium": 2, "Hard": 3}[difficulty]

    def get_final_scores(self):
        return sorted(self.players.values(), key=lambda x: x['score'], reverse=True)


async def display_leaderboard(ctx):
    leaderboard = db.get_trivia_leaderboard()
    embed = hikari.Embed(title="WoW Trivia Leaderboard", color=0x00ff00)
    embed.set_thumbnail("img/orc presentation.png")  # Replace with an actual WoW trivia logo

    for i, (username, score) in enumerate(leaderboard, 1):
        emoji = get_rank_emoji(i, len(leaderboard))
        embed.add_field(name=f"{emoji} {username}", value=f"Score: {score}", inline=False)

    await ctx.respond(embed=embed)