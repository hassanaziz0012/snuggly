from typing import Optional, List
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import View
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database as MongoDatabase
from utils import parse_date_string, convert_date_to_readable_form
from datetime import datetime
from typing import Union
import discord
import logging
import emoji


logger = logging.getLogger('snuggly')

class Database:
    @staticmethod
    def create_connection() -> MongoDatabase:
        client = MongoClient(host="localhost", port=27017)
        bot_db = client.snuggly
        return bot_db

    @staticmethod
    def create_poll(user_id: int, user: str, title: str, choices: list, expiry_date: datetime):
        db = Database.create_connection()
        polls_col = db.polls
        result = polls_col.insert_one({
            "user_id": user_id,
            "user": user,
            "title": title,
            "choices": choices,
            "expiry_date": expiry_date,
        })
        return result.acknowledged

    @staticmethod
    def get_polls():
        db = Database.create_connection()
        polls_col = db.polls
        return polls_col.find()


class PollingCog(commands.Cog, name="Polls"):
    # TODO: Need to add an event that automatically expires polls, disables reacts on the poll message, and displays the poll results, and then finally deletes the poll from our database.
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command("poll")
    @commands.has_permissions(administrator=True)
    async def create_poll(self, ctx: Context, title: str, channel: discord.TextChannel = None, expiry_date: str = None):
        """
        Create a poll in the specified channel. Requires administrator permissions.

        Usage:
        .poll Poll title text  #channel 1d24h60m

        If channel is not specified, the poll will be posted in the current channel.
        If expiry_date is not specified, the poll will expire in 24 hours by default.
        """
        await ctx.send(f"Creating poll: {title} - Please type the list of choices (comma-separated). Please also add an emoji per choice, so users can select a choice.")

        def check(msg: discord.Message):
            if msg.author == ctx.author and msg.channel == ctx.channel:
                return True
            else:
                return False

        msg = await self.bot.wait_for("message", check=check)
        choices: List[str] = msg.content.split(',')
        parsed_choices = []
        for choice in choices:
            emojis = [emote for emote in choice if emote in emoji.UNICODE_EMOJI['en']]
            if len(emojis) > 0:
                choice_text = ''.join([c for c in choice.strip() if c not in emojis])
                parsed_choices.append({"text": choice_text, "emoji": emojis[0]})
            else:
                await ctx.send("Please add an emoji for the choice: " + choice)

        if len(choices) != len(parsed_choices):
            await ctx.send("Command exiting. Please correct the above errors.")
            return

        nl = "\n" # Have to do this because using backslashes in f-strings isn't allowed in Python.
        print(channel)
        description = f"""
Available options:
{nl.join([f"{i}) {choice['text']} {choice['emoji']}" for i, choice in enumerate(parsed_choices, start=1)])}
        """
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        if channel:
            message = await channel.send(embed=embed)
        else:
            message = await ctx.send(embed=embed)

        for choice in parsed_choices:
            await message.add_reaction(choice['emoji'])
        
        if expiry_date == None:
            parsed_date = "1d"
        else:
            parsed_date = parse_date_string(expiry_date)

        result = Database.create_poll(
            user_id=int(ctx.message.author.id),
            user=str(ctx.message.author),
            title=title,
            choices=parsed_choices,
            expiry_date=parsed_date
        )
        print(result)


    @create_poll.error
    async def create_poll_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"Please specify the poll title.")
        else:
            print(error, ctx)

    @commands.command(name="polls")
    @commands.has_permissions(administrator=True)
    async def get_polls(self, ctx):
        polls = Database.get_polls()
        if polls:
            description = '\n'.join([
                f"\"{poll['title']}\" created by {poll['user']}, expires at {convert_date_to_readable_form(poll['expiry_date'])}" for i, poll in enumerate(polls, start=1)
                ])
            print(description)
        embed = discord.Embed(title="Polls", description=description, color=discord.Color.blurple())
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(PollingCog(client))
