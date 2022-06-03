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
    description='Help me ˊ ˋ',
    intents=intents,
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.load_extension('cogs')

bot.run(token)