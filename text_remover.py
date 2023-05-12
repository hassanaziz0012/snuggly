from discord.ext import commands
import discord
import re


class TextCog(commands.Cog, name="Text Stuff"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def remove_urls(self, ctx):
        """
        Removes all URLs from the entire server. 
        """
        await ctx.send("Scanning server contents. May take a while...")
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                async for message in channel.history(limit=1000):
                    regex = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
                    match = re.search(regex, message.content)
                    if match:
                        await message.delete()
        await ctx.send("Command finished.")

    @commands.command()
    async def copy_urls(self, ctx):
        """
        Copies all URLs from the entire server and shows you the list. This is best used before the 'remove_urls' command to ensure you don't nuke your server. 
        """
        await ctx.send("Scanning server contents. May take a while...")
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                async for message in channel.history(limit=1000):
                    regex = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
                    match = re.search(regex, message.content)
                    if match:
                        await ctx.send(message.content)
        await ctx.send("Command finished.")

    @commands.command()
    async def remove_text(self, ctx, text: str):
        """
        Removes all matches of the specified text from the entire server. 
        """
        await ctx.send("Scanning server contents. May take a while...")
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                async for message in channel.history(limit=1000):
                    if text in message.content:
                        await message.delete()
        await ctx.send("Command finished.")

async def setup(client):
    await client.add_cog(TextCog(client))
