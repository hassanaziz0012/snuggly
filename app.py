from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import discord
import os
import logging
import sys


discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', date_format, style="{")
handler.setFormatter(formatter)
discord_logger.addHandler(handler)

snuggly_logger = logging.getLogger('snuggly')
snuggly_logger.setLevel(logging.INFO)
snuggly_logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=".", intents=intents)
load_dotenv()
token = os.environ.get('TOKEN')


@client.event
async def on_ready():
    # TODO: There's gotta be a better way of doing this. Find it.
    # We're basically using the on_ready event to check for due reminders.
    snuggly_logger.info("Bot is ready")
    # print("Checking for reminders every 3 seconds...")
    # while True:
    #     due_reminders = await RemindersCog.check_for_due_reminders()
    #     if due_reminders is not None:
    #         general_channel = client.get_channel(832222029075447871)
    #         for reminder in due_reminders:
    #             user = client.get_user(int(reminder[2]))
    #             await general_channel.send(f"{reminder[3]} is due! {user.mention}")
    #             await RemindersCog.remove_due_reminders(reminder)

    #     await asyncio.sleep(3)

@client.command()
async def greet(ctx):
    await ctx.send("Hello!")


async def load_extensions():
    # Loading all bot extensions...
    await client.load_extension("google_apis")
    await client.load_extension("note_taking")
    await client.load_extension("reminders")
    await client.load_extension("misc")
    await client.load_extension("text_remover")
    await client.load_extension("polling")

async def main():
    async with client:
        await load_extensions()
        await client.start(token)

asyncio.run(main())
