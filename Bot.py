#! /usr/bin/env python3
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

#Get API token from the .env file
token = os.getenv("token")

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description='碼農',
    intents=intents,
)

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening ,name="Flamingo"))
    print(f'Logged in as {bot.user}')
    print('--------------------------')

@bot.command()
@commands.is_owner()
async def load(ctx, extention):
    """
    Load an extention
    """

    bot.load_extension(f'cogs.{extention}')
    await ctx.send(f'**Loaded {extention}**')

@bot.command()
@commands.is_owner()
async def unload(ctx, extention):
    """
    Unload an extention
    """

    bot.unload_extension(f'cogs.{extention}')
    await ctx.send(f'**Unloaded {extention}**')

@bot.command()
@commands.is_owner()
async def reload(ctx, extention):
    """
    Reload an extention
    """

    bot.reload_extension(f'cogs.{extention}')
    await ctx.send(f'**Reloaded {extention}**')

@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)}ms') # Already changed to micro second

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    bot.run(token)