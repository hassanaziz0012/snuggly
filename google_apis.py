from utils import (
    change_file_permissions_to_anyone,
    delete_downloaded_files,
    delete_file_from_google_drive,
    download_attachment,
    upload_to_gdrive,
)
import discord
from discord.errors import HTTPException
from zipfile import ZipFile
import asyncio
from discord.ext import commands


class GoogleAPIsCog(commands.Cog, name="Google APIs"):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=["download-attachments", "dl-attachments"])
    async def download_attachments(self, ctx, channel: discord.TextChannel):
        """
        Downloads all attachments in the specified channel.
        """
        if channel == None:
            await ctx.send("Please specify a channel.")
            return

        await ctx.send(
            "Downloading attachments from this channel. This may take a long time. Please wait."
        )
        with ZipFile(f"{channel.name} - Attachments.zip", "w") as zip:
            async for message in channel.history(limit=200):
                for i, attachment in enumerate(message.attachments):
                    file_name = download_attachment(i, attachment)
                    print(f"Adding {file_name} to archive...")
                    zip.write(file_name)
                    asyncio.sleep(0.1)

            await ctx.send(
                "Downloaded and Archived all attachments from this channel. Uploading .zip archive to Discord..."
            )
            zip.close()

            # Discord only allows file uploads of 8MB maximum. So, we check if our file is too large. It will raise the HTTPException error if the filesize is too large.
            # If it is too large, we will upload to Google Drive instead, and will give the user a temporary link to download the file. This link will expire in 1 hour
            # and the file will be deleted.
            try:
                await ctx.send(file=discord.File(f"{channel.name} - Attachments.zip"))
            except HTTPException:
                await ctx.send(
                    "File is too large to upload to Discord. Uploading to Google Drive..."
                )

                result = upload_to_gdrive(zip)
                await ctx.send(
                    embed=discord.Embed(
                        description=f"Finished uploading to Google Drive. Please go to the following link to download the file:\n{result['download_link']}\n\nThis link will automatically expire after **1 hour**."
                    )
                )

                # Change perms so anyone can see and download the file.
                change_file_permissions_to_anyone(result["file_id"])

                # Delete file from GDrive after one hour.
                await asyncio.sleep(86400)
                delete_file_from_google_drive(result["file_id"])

        # Deleting downloaded files so we don't waste precious space.
        delete_downloaded_files()

    @download_attachments.error
    async def on_command_error(self, ctx, error):
        await ctx.send("Please specify a channel.")

async def setup(client):
    await client.add_cog(GoogleAPIsCog(client))
