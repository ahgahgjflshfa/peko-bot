import asyncio
import discord
from discord.ext import commands
import youtube_dl
from requests import get

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Joins a voice channel")
    async def join(self, ctx):
        #Joins the channel

        if not ctx.message.author.voice:
            await ctx.send(f"請先加入語音頻道！")
            return

        else:
            channel = ctx.message.author.voice.channel

        await channel.connect()

    @commands.command(description="Leaves the voice channel")
    async def leave(self, ctx):
        #Leave the voice channel

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()

        else:
            await ctx.send("沒有連接至任何語音頻道！使用join來讓機器人加入頻道")

    @commands.command(description="Plays the music (Bot will have to download the w4a file first)")
    async def play(self, ctx, *, url):
        #Plays the music

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'**正在播放**: {player.title}')

    '''@commands.command(name='loop', help='This command toggles loop mode')
    async def loop_(ctx):
        global loop

        if loop:
            await ctx.send('Loop mode is now `False!`')
            loop = False
        
        else: 
            await ctx.send('Loop mode is now `True!`')
            loop = True'''

    @commands.command(description="Pause the music")
    async def pause(self, ctx):
        #Pause the music

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()

        else:
            await ctx.send("機器人沒有在播放音樂！")

    @commands.command(description="Resume the music")
    async def resume(self, ctx):
        #Resume the music

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        
        else:
            await ctx.send("之前沒有在播放音樂！使用play來播放音樂")

    @commands.command(description="Stops the music")
    async def stop(self, ctx):
        #Stops the music

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        
        else:
            await ctx.send("機器人沒有在播放音樂！")

intents = discord.Intents().all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents
)

def setup(bot):
    bot.add_cog(Music(bot))