from typing import List
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import sqlite3
import re
import calendar


class Database:
    "This class contains all the methods that involve interacting and working with the database. The bot commands simply call these methods to perform operations on the database."

    @staticmethod
    def create_connection(db_file=r"database\reminders.db") -> sqlite3.Connection:
        "Create a database connection to a SQLite database. Returns an sqlite3.Connection object."
        conn = None
        try:
            conn = sqlite3.connect(
                db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            Database.create_required_tables(conn)
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                return conn

    @staticmethod
    def create_required_tables(conn: sqlite3.Connection) -> None:
        """
        Creates a table called 'reminders' in the database. Takes in a 'sqlite.Connection' object and executes the SQL code to create the necessary tables.
        This function is automatically called as soon as a connection is created, in the Database.create_connection() function.
        """
        try:
            c = conn.cursor()

            sql_code = """CREATE TABLE IF NOT EXISTS reminders (
                id integer PRIMARY KEY,
                user text NOT NULL,
                user_id integer NOT NULL,
                reminder text NOT NULL,
                time timestamp NOT NULL
                );"""

            c.execute(sql_code)
            conn.commit()

        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def check_reminders(user_id: int) -> List:
        """
        Retrieves the 'reminders' from the database which belong to the given user and returns them as a List object.
        param <user_id>: An integer that contains the user's ID, which is like a very long number.
        """
        try:
            conn = Database.create_connection()

            c = conn.cursor()
            sql_code = f"""SELECT * FROM reminders WHERE user_id=?"""
            c.execute(sql_code, (user_id,))

            rows = c.fetchall()
            return rows

        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def get_all_reminders() -> List:
        "Retrieves all 'reminders' from the database and returns them as a List object."
        try:
            conn = Database.create_connection()

            c = conn.cursor()
            sql_code = f"""SELECT * FROM reminders"""
            c.execute(sql_code)

            rows = c.fetchall()
            return rows

        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def listen_for_due_reminders():
        "An asynchronous function that will check all reminders in the database for when one of them is due, and then alert the user. THIS FUNCTION IS INCOMPLETE AS OF YET!"
        rows = Database.get_all_reminders()
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
        try:
            conn = Database.create_connection()
            c = conn.cursor()
            sql_code = (
                f"""INSERT INTO reminders(user,user_id,reminder,time) VALUES(?,?,?,?)"""
            )
            values = (user, user_id, reminder, time)

            c.execute(sql_code, values)

            conn.commit()
            conn.close()

            return c.lastrowid
        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def remove_reminder(reminder: str, user_id: int):
        """
        Removes a reminder from the database file.

        param <reminder>: A string that contains the reminder text, exactly as is stored in the database.
        param <user_id>: An integer that contains the user's ID, which is like a very long number.
        """
        try:
            conn = Database.create_connection()
            c = conn.cursor()
            sql_code = f"""DELETE FROM reminders WHERE reminder = ? AND user_id = ?"""

            c.execute(
                sql_code,
                (
                    reminder,
                    user_id,
                ),
            )
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(e)


class Utilities:
    "Contains a bunch of helper functions for the reminders.py file."

    @staticmethod
    def convert_date_to_readable_form(date):
        date_in_readable_form = (
            calendar.month_name[date.month] + " " + str(date.day) + " " + str(date.year)
        )
        time_in_readable_form = (
            str(date.hour) + ":" + str(date.minute) + ":" + str(date.second)
        )

        result = str(date_in_readable_form) + " - " + str(time_in_readable_form)
        return result

class RemindersCog(commands.Cog, name="Reminders"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=["reminder"])
    async def create_reminder(self, ctx, time, reminder):
        """
        Create a new reminder.

        Usage:
        > .create_reminder 1d6h "Do things"
        This will remind you in 1 day and 6 hours.
        """

        try:
            # Read the "time" argument to figure out how many days, hours, and minutes until we remind the user.
            days, hours, minutes = None, None, None
            if "d" in time:
                pattern = "\d+d"
                match = re.search(pattern, time)
                days = str(match.group()).replace("d", "")

            if "h" in time:
                print(time)
                pattern = "\d+h"
                match = re.search(pattern, time, flags=re.IGNORECASE)
                hours = str(match.group()).replace("h", "")

            if "m" in time:
                pattern = "\d+m"
                match = re.search(pattern, time)
                minutes = str(match.group()).replace("m", "")

            # There is a possibility that the user does not enter a day or an hour or a minute. We check for that possiblity here using ternary operators.
            reminder_date = datetime.today() + timedelta(
                days=int(days if days else 0),
                hours=int(hours if hours else 0),
                minutes=int(minutes if minutes else 0),
            )

        except Exception as e:
            await ctx.send(
                embed=discord.Embed(
                    description=f"You have provided an invalid date and time. Please try again. The actual error is reproduced below:\n\n\{e}"
                )
            )

        # We convert the reminder_date into a more readable form, which will be given to the user.
        reminder_date_in_readable_form = Utilities.convert_date_to_readable_form(
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


    @commands.command(aliases=["reminders"])
    async def read_reminders(self, ctx):
        """
        Check all reminders you currently have.
        """
        rows = Database.check_reminders(user_id=str(ctx.message.author.id))
        items = []

        if rows:
            for row in rows:
                date_str = Utilities.convert_date_to_readable_form(row[4])
                items.append(f"({row[0]}) {row[3]} due at **{date_str}**")
            embed = discord.Embed(
                description=f"**Reminders for {ctx.message.author.mention}**\n\n"
                + "\n".join(items)
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
        rows = Database.get_all_reminders()
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
