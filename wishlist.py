# Contains the commands for the wishlist features of the bot.
import sqlite3
import discord
from discord.ext import commands


class Database:
    @staticmethod
    def create_connection(db_file=r"database\wishlist.db"):
        "Create a database connection to a SQLite database"
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            Database.create_required_tables(conn)
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                return conn

    @staticmethod
    def create_required_tables(conn):
        "This function creates the 'wishlist' table in the database. This table is where we store all data regarding the wishlists features of our app."
        try:
            c = conn.cursor()

            sql_code = """CREATE TABLE IF NOT EXISTS wishlists (
                id integer PRIMARY KEY,
                item_name text NOT NULL,
                item_url text,
                user text NOT NULL,
                user_id integer NOT NULL
                );"""

            c.execute(sql_code)
            conn.commit()

        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def check_wishlist(user_id: int):
        "This function retrieves all items from the wishlist of the user with the given 'user_id'."
        try:
            conn = Database.create_connection()

            c = conn.cursor()
            sql_code = f"""SELECT * FROM wishlists WHERE user_id=?"""
            c.execute(sql_code, (user_id,))

            rows = c.fetchall()
            return rows

        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def select_item(user_id: int, item_name: str):
        "This function is used to select a single item."
        try:
            conn = Database.create_connection()

            c = conn.cursor()
            sql_code = f"""SELECT * FROM wishlists WHERE user_id=? AND item_name=?"""
            c.execute(sql_code, (user_id, item_name))

            rows = c.fetchall()
            return rows

        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def add_to_wishlist(user: str, user_id: int, item_name: str, item_url):
        "This function adds a new wishlist item to the database."
        try:
            conn = Database.create_connection()
            c = conn.cursor()
            sql_code = f"""INSERT INTO wishlists(item_name,item_url,user,user_id) VALUES(?,?,?,?)"""
            values = (item_name, item_url, user, user_id)

            c.execute(sql_code, values)
            conn.commit()
            conn.close()

            return c.lastrowid
        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def remove_from_wishlist(item_name: str, user_id: int):
        "This function removes an item from the wishlist of the user who sent the command."
        try:
            conn = Database.create_connection()
            c = conn.cursor()
            sql_code = f"""DELETE FROM wishlists WHERE item_name = ? AND user_id = ?"""

            c.execute(
                sql_code,
                (
                    item_name,
                    user_id,
                ),
            )
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(e)


class WishlistCog(commands.Cog, name="Wishlist"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=["wishlist"])
    async def check_wishlist(self, ctx):
        """
        Retrieves all items in your wishlist.
        """
        rows = Database.check_wishlist(user_id=int(ctx.message.author.id))
        items = []
        if rows:
            for row in rows:
                # 0 = ID, 1 = Item Name, 2 = Item URL, and 3 (which we don't print) = User's name
                items.append(f"({row[0]}) {row[1]} - {row[2]}")

        embed = discord.Embed()
        embed.description = (
            f"Your wishlist currently has the following items:\n\n" + "\n".join(items)
        )
        await ctx.send(embed=embed)


    @commands.command(aliases=["add-to-wishlist", "add-to-wl"])
    async def add_to_wishlist(self, ctx, item_name: str = None, *, item_url: str = None):
        """
        Adds the specified item to your wishlist. 

        Usage:
        > .add_to_wishlist "Item Name" "Item URL"
        """
        if item_name is not None:
            Database.add_to_wishlist(
                user=str(ctx.message.author),
                user_id=int(ctx.message.author.id),
                item_name=str(item_name),
                item_url=item_url,
            )
            embed = discord.Embed()
            embed.description = f"Added the following item to your wishlist:\n{item_name} - Link: {item_url}"

            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description='You forgot to enter a name for your item. Please try again, and type a name this time. The name should be enclosed in double quotes, such as, "Name goes here".'
                )
            )


    @commands.command(aliases=["delete-from-wl", "remove-from-wl"])
    async def remove_from_wishlist(self, ctx, item_name: str = None):
        """
        Removes the item specified from your wishlist. 
        
        Just type the item name with this command.
        """
        if item_name is not None:
            selected_item = Database.select_item(
                user_id=int(ctx.message.author.id), item_name=item_name
            )
            if selected_item is not None:
                Database.remove_from_wishlist(
                    item_name=str(item_name), user_id=int(ctx.message.author.id)
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        description="The item name you provided does not match any item in your account. Please type the correct name and try again."
                    )
                )
                return

            embed = discord.Embed(
                description=f"{item_name} has been successfully removed from your wishlist."
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="You did not enter the name of the item which should be removed. Please try again, and type a name this time."
                )
            )


async def setup(client):
    await client.add_cog(WishlistCog(client))
