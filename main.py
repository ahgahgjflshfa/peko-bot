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

bot.load_extension('cogs/Music')
bot.load_extension('cogs/Help')

bot.run(token)