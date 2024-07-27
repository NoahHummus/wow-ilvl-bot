import asyncio
import re
import textwrap

import hikari
import lightbulb

import chatgptPy
import db
from main import get_all_character_data, extract_duel_relevant_data


class DuelSelectionMenu(hikari.ComponentInteraction):
    def __init__(self, custom_id: str):
        super().__init__(custom_id)
        self.selected_characters = []

    async def callback(self, ctx: lightbulb.Context) -> None:
        if len(self.selected_characters) < 2:
            selected = ctx.interaction.values[0]
            character_name, realm = selected.split("|")
            self.selected_characters.append((character_name, realm))

            if len(self.selected_characters) == 1:
                await ctx.respond("First character selected. Please choose the second character.")
            elif len(self.selected_characters) == 2:
                await ctx.respond("Both characters selected. Initiating duel...")
                await initiate_duel(ctx, self.selected_characters[0], self.selected_characters[1])
        else:
            await ctx.respond("You've already selected two characters. Please start a new duel.")


async def initiate_duel(ctx, character1, character2):
    await ctx.respond("Fetching character data and preparing the arena for an epic duel...")

    try:
        character1_data = get_all_character_data(character1['realm'], character1['name'])
        character2_data = get_all_character_data(character2['realm'], character2['name'])

        character1_info = extract_duel_relevant_data(character1_data)
        character2_info = extract_duel_relevant_data(character2_data)

        # Save character renders to the database
        db.save_character_render(character1['name'], character1_info['character_render'])
        db.save_character_render(character2['name'], character2_info['character_render'])

        narrative = chatgptPy.generate_duel_narrative(character1_info, character2_info)

        # Split the narrative into introduction, rounds, and conclusion
        parts = re.split(r'(Round \d+|WINNER:)', narrative)
        introduction = parts[0].strip()
        rounds = [parts[i:i + 2] for i in range(1, len(parts) - 1, 2) if parts[i].startswith("Round")]
        winner = parts[-1].strip() if parts[-2] == "WINNER:" else "Unknown"

        # Create the main embed
        embed = hikari.Embed(
            title=f"Duel between this fucker: {character1['name']} and this dumbass fucker: {character2['name']}",
            description=introduction[:2048],  # Discord's limit for embed description
            color=hikari.Color(0x00ff00)
        )

        # Set character renders
        render_url1 = db.get_character_render(character1['name'])
        render_url2 = db.get_character_render(character2['name'])
        if render_url1:
            embed.set_thumbnail(render_url1)
        if render_url2:
            embed.set_image(render_url2)

        # Add rounds to embed
        for round_title, round_text in rounds:
            # Split the round text into chunks of 1024 characters
            chunks = textwrap.wrap(round_text.strip(), 1024, break_long_words=False, replace_whitespace=False)
            for i, chunk in enumerate(chunks):
                if i == 0:
                    embed.add_field(name=round_title.strip(':'), value=chunk, inline=False)
                else:
                    embed.add_field(name=f"{round_title.strip(':')} (continued)", value=chunk, inline=False)

        # Add winner
        embed.add_field(name="🏆 Victor", value=f"**{winner}** emerges victorious!", inline=False)

        # Record the duel result
        db.record_duel_result(winner,
                              character2['name'] if winner.lower() == character1['name'].lower() else character1['name'])

        await ctx.respond(embed=embed)

    except Exception as e:
        await ctx.respond(f"An error occurred: {str(e)}")


def extract_winner(narrative):
    try:
        lines = narrative.split('\n')
        for line in reversed(lines):  # Start from the end of the narrative
            if line.startswith("WINNER:"):
                return line.split(":")[1].strip()
    except Exception as e:
        print(f"Error extracting winner: {str(e)}")
    return "Unknown"  # In case the winner can't be determined


async def handle_character_selection(ctx, interaction):
    selected = interaction.values[0]
    character_name, realm = selected.split("|")

    if not hasattr(ctx, "selected_characters"):
        ctx.selected_characters = []

    ctx.selected_characters.append((character_name, realm))

    if len(ctx.selected_characters) == 1:
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_UPDATE,
            "First character selected. Please choose the second character.",
            components=[interaction.message.components[0]]
        )
    elif len(ctx.selected_characters) == 2:
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_UPDATE,
            "Both characters selected. Initiating duel...",
            components=[]
        )
        await initiate_duel(ctx, ctx.selected_characters[0], ctx.selected_characters[1])
    else:
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_UPDATE,
            "You've already selected two characters. Please start a new duel.",
            components=[]
        )