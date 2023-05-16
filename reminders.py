from typing import List
from discord.ext import commands
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database as MongoDatabase
from utils import parse_date_string, convert_date_to_readable_form
import sqlite3
import re
import discord
import calendar


class Database:
    "This class contains all the methods that involve interacting and working with the database. The bot commands simply call these methods to perform operations on the database."

    @staticmethod
    def create_connection() -> MongoDatabase:
        client = MongoClient(host="localhost", port=27017)
        bot_db = client.snuggly
        return bot_db

    @staticmethod
    def check_reminders(user_id: int) -> List:
        """
        Retrieves the 'reminders' from the database which belong to the given user and returns them as a List object.
        param <user_id>: An integer that contains the user's ID, which is like a very long number.
        """
        db = Database.create_connection()
        reminders_col = db.reminders
        c = reminders_col.find({"user_id": int(user_id)})
        return c

    @staticmethod
    def _get_all_reminders() -> List:
        db = Database.create_connection()
        reminders_col = db.reminders
        c = reminders_col.find()
        return c

    @staticmethod
    def listen_for_due_reminders():
        """
        An asynchronous function that will check all reminders in the database for when one of them is due, 
        and then alert the user.
        
        THIS FUNCTION IS INCOMPLETE AS OF YET!
        """
        # TODO: Finish this.
        rows = Database._get_all_reminders()
        for row in rows:
            user = row[1]
            reminder = row[2]
            time = row[3]

    @staticmethod
    def add_reminder(user: str, user_id: int, reminder: str, time: str) -> int:
        """
        Adds a reminder to the database file.

        param <user_id>: An integer that contains the user's ID, which is like a very long number.
        param <user>: A string that contains the User's name and discord tag, for example Hassan#3557.
        param <reminder>: A string that contains the reminder text, exactly as is stored in the database.
        param <time>: A string that contains the time until we remind the user, for example '2d5h16m' is 2 days, 5 hours, and 16 minutes.
        """
        db = Database.create_connection()
        reminders_col = db.reminders
        result = reminders_col.insert_one({
            "user_id": user_id,
            "user": user,
            "reminder": reminder,
            "time": time
        })

        return result.acknowledged


    @staticmethod
    def remove_reminder(reminder: str, user_id: int):
        """
        Removes a reminder from the database file.

        param <reminder>: A string that contains the reminder text, exactly as is stored in the database.
        param <user_id>: An integer that contains the user's ID, which is like a very long number.
        """
        db = Database.create_connection()
        reminders_col = db.reminders
        result = reminders_col.delete_one({'reminder': reminder, 'user_id': user_id})
        return result.acknowledged


class RemindersCog(commands.Cog, name="Reminders"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=["reminder"])
    async def create_reminder(self, ctx, time, *, reminder):
        """
        Create a new reminder.

        Usage:
        > .create_reminder 1d6h "Do things"
        This will remind you in 1 day and 6 hours.
        """

        try:
            reminder_date = parse_date_string(time)
        except Exception as e:
            await ctx.send(
                embed=discord.Embed(
                    description=f"You have provided an invalid date and time. Please try again. The actual error is reproduced below:\n\n\{e}"
                )
            )

        # We convert the reminder_date into a more readable form, which will be given to the user.
        reminder_date_in_readable_form = convert_date_to_readable_form(
            reminder_date
        )

        Database.add_reminder(
            user=str(ctx.message.author),
            user_id=int(ctx.message.author.id),
            reminder=reminder,
            time=reminder_date,
        )

        embed = discord.Embed(
            description=f'Created reminder *"{reminder}"* due on **{reminder_date_in_readable_form}**'
        )
        await ctx.send(embed=embed)

    @create_reminder.error
    async def create_reminder_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = discord.Embed(title="Error", description=f"Please specify the: {error.param}", color=discord.Color.red())
            await ctx.send(embed=embed)


    @commands.command(aliases=["reminders"])
    async def read_reminders(self, ctx):
        """
        Check all reminders you currently have.
        """
        rows = Database.check_reminders(user_id=ctx.message.author.id)
        items = []

        if rows:
            for row in rows:
                date_str = convert_date_to_readable_form(row['time'])
                items.append(f"{row['reminder'].capitalize()} due at **{date_str}**")
            embed = discord.Embed(
                description=f"**Reminders for {ctx.message.author.mention}**\n\n"
                + "\n".join(items), color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f"No reminders for {ctx.message.author.mention}."
                )
            )


    @commands.command(aliases=["rm-reminder"])
    async def remove_reminder(self, ctx, reminder):
        """
        This command is incomplete and under construction!
        """
        pass

    @staticmethod
    async def check_for_due_reminders():
        rows = Database._get_all_reminders()
        due_reminders = []
        if rows:
            for row in rows:
                date_str = row[4]
                if date_str <= datetime.now():
                    due_reminders.append(row)
            return due_reminders
        else:
            return None

    @staticmethod
    async def remove_due_reminders(reminder: List):
        Database.remove_reminder(reminder=reminder[3], user_id=reminder[2])


async def setup(client):
    await client.add_cog(RemindersCog(client))
