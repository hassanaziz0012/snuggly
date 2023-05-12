from discord.ext import commands
import discord
import random
import os
import psycopg2


class MiscCog(commands.Cog, name="Misc"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def clear(self, ctx, amount: int = 5):
        """
        Clear X messages from the channel. 
        
        Defaults to 5 messages if the amount isn't specified.
        """
        await ctx.channel.purge(limit=amount)


    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kick a member from the server. Optionally provide a reason as well.

        Usage:
        > .kick @Member#0000 "Reason: Because I can"
        """
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} was kicked for the following reason:\n{reason}")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Please mention the user you want to kick.")

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question=None):
        """
        Ask the mighty 8 Ball a question!
        """
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        if question is not None:
            await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="**8 Ball:** You need to give a question as well."
                )
            )


async def setup(client):
    await client.add_cog(MiscCog(client))
