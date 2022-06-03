import asyncio
import discord
from discord.ext import commands
import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ''

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
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
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        if not ctx.message.author.voice:
            ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return

        else:
            channel = ctx.message.author.voice.channel

        await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        #let the bot leave the channel
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()

        else:
            await ctx.send("沒有連接至任何語音頻道！使用join來讓機器人加入頻道")

    @commands.command()
    async def play(self, ctx, *, url):
        #play from url
        try:
            voice_channel = ctx.message.guild.voice_client
            

            async with ctx.typing():
                filename = await YTDLSource.from_url(url, loop=self.bot.loop)
                voice_channel.play(discord.FFmpegAudio(executable="ffmpeg.exe", source=filename))

            await ctx.send(f"**正在播放** {filename}")

        except:
            await ctx.send("機器人沒有連到任何頻道！使用join來讓機器人加入頻道")

    @commands.command()
    async def stream(self, ctx, url):
        #play without download
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.message.voice_client
        if voice_client.is_playing():
            await voice_client.pause()

        else:
            await ctx.send("機器人沒有在播放音樂！")

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        
        else:
            await ctx.send("之前沒有在播放音樂！使用play來播放音樂")

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        
        else:
            await ctx.send("機器人沒有在播放音樂！")

intents = discord.Intents().all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents
)

def setup(bot):
    bot.add_cog(Music(bot))