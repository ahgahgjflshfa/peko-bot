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
    description='学校はマジで嫌いですわ～',
    intents=intents,
)

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening ,name="Flamingo"))
    print(f'Logged in as {bot.user}')
    print('--------------------------')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    bot.run(token)