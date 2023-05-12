# Contains the commands for the note-taking features of the bot.
import sqlite3
from typing import List, Tuple
import discord
from discord.ext import commands
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database as MongoDatabase


class Database:
    "This class contains all the methods that involve interacting and working with the database. The bot commands simply call these methods to perform operations on the database."

    @staticmethod
    def create_connection() -> MongoDatabase:
        client = MongoClient(host="localhost", port=27017)
        bot_db = client.hassanbot
        return bot_db


    @staticmethod
    def check_notes(user_id: int) -> Cursor:
        db = Database.create_connection()
        notes_coll = db.notes
        c = notes_coll.find({"user_id": user_id})
        return c            
        

    @staticmethod
    def read_note(user_id: int, title: str) -> dict:
        db = Database.create_connection()
        notes_coll = db.notes
        note = notes_coll.find_one({"user_id": user_id, "title": title})
        return note


    @staticmethod
    def add_note(user_id: int, user: str, title: str, content: str) -> bool:
        db = Database.create_connection()
        notes_coll = db.notes
        result = notes_coll.insert_one({
            "user_id": user_id,
            "user": user,
            "title": title,
            "content": content
        })

        return result.acknowledged

    @staticmethod
    def remove_note(title: str, user_id: int) -> bool:
        db = Database.create_connection()
        notes_coll = db.notes
        result = notes_coll.delete_one({"title": title})
        return result.acknowledged

class NotesCog(commands.Cog, name="Notes"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=["notes"])
    async def check_notes(self, ctx):
        """
        Get all the notes stored in your account.
        """
        c = Database.check_notes(user_id=int(ctx.message.author.id))

        items = []
        if c:
            for i, note in enumerate(c, start=1):
                items.append(f"({i}) {note['title']}")

        embed = discord.Embed(description="**YOUR NOTES:**\n\n" + "\n".join(items))
        await ctx.send(embed=embed)


    @commands.command(aliases=["note"])
    async def read_note(self, ctx, title: str = None):
        """
        Read a specific note in your collection.

        Usage:
        > .read_note "Note Title"
        """
        if title is not None:
            note = Database.read_note(user_id=int(ctx.message.author.id), title=title)
            if note is not None:
                embed = discord.Embed(description=f"**{note['title']}**\n\n{note['content']}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description="Either this note does not exist or you entered the wrong title. Try again."
                    )
                )
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="You forgot to enter a title. You need to type the title of the note."
                )
            )


    @commands.command(aliases=["writenote"])
    async def write_note(self, ctx, title: str = None, *, content: str = None):
        """
        Add a new note to your collection. 

        Provide the title and the content for the note as well.

        Usage:
        > .write_note "Title goes here" "Content goes here"
        """
        if title is not None and content is not None:
            Database.add_note(
                user=str(ctx.message.author),
                user_id=int(ctx.message.author.id),
                title=title,
                content=content,
            )

            embed = discord.Embed(description=f"**{title}**\n\n{content}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="""
                        You forgot to enter either a title or some content for this note. Please try again and enter both a title and the content for this note. 
                        \nRemember that the title should be enclosed in double quotes, such as, "Title goes here". You don\'t have to enclose the content in double quotes.
                        """
                )
            )


    @commands.command(aliases=["removenote"])
    async def remove_note(self, ctx, title=None):
        """
        This function is used to remove a note from the database.

        param <title>: A string that uniquely identifies the note. Each note has a title.
        """
        if title is not None:
            selected_note = Database.read_note(
                user_id=int(ctx.message.author.id), title=title
            )
            if selected_note is not None:
                Database.remove_note(title=title, user_id=int(ctx.message.author.id))
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description="The title you entered does not match any existing note. Please try again."
                    )
                )
                return

            embed = discord.Embed(description=f"**{title}** has been removed!")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="You did not enter a title. Please enter the title of the note you want to delete."
                )
            )


async def setup(client):
    await client.add_cog(NotesCog(client))
