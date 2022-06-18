#! /usr/bin/env python3
#encoding: utf-8

import discord
from discord.ext import commands
import youtube_dl
from requests import get
import asyncio
from random import shuffle
import os
from core.classes import Cog_Extension

youtube_dl.utils.bug_reports_message = lambda: ''

# Global variables

Root_Dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': f'{Root_Dir}/audio files/%(extractor)s-%(id)s-%(title)s.%(ext)s',
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

FFMPEG_OPTS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queue = []

local_queue = []

now_playing = ''

download_filename = ''

# Functions

def search(query):
    with youtube_dl.YoutubeDL({'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}) as ydl:
        try: get(query)
        except: info = ydl.extract_info(f'ytsearch:{query}', download=False)['entries'][0]
        else: info = ydl.extract_info(query, download=False)
    
    return (info, info['formats'][0]['url'])

async def join(ctx):
    channel = ctx.message.author.voice.channel

    await channel.connect()

def check_queue(ctx):
    if queue:
        url = queue.pop(0)

        global now_playing
        now_playing = search(url)[0]["title"]

        ctx.message.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(search(url)[1], **FFMPEG_OPTS), 0.1), after=lambda x: check_queue(ctx))

def local_queue_init(playlist):
    
    if not os.path.isfile(f"{Root_Dir}/playlists/{playlist}.txt"):
        return False
    
    with open(f"{Root_Dir}/playlists/{playlist}.txt", "r") as f:
        f.seek(0)
        
        global local_queue
        local_queue = [ s.rstrip('\n') for s in f.readlines() ]
        
    return True

def check_local_queue(ctx):
    if local_queue:
        audio = local_queue.pop(0)
        
        ctx.message.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="ffmpeg", source=f'{Root_Dir}/audio files/' + audio.rstrip('\n')), volume=0.1), after=lambda x: check_local_queue(ctx))

# ?

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
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

        global filename

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable="ffmpeg", **ffmpeg_options), data=data)

# Discord commands

class Music(Cog_Extension):
    """
    Music命令ですわ～
    """

    @commands.command(help='Format: !play <url>\nStream from url')
    async def play(self, ctx, *, url):
        
        if not ctx.message.author.voice:
            await ctx.send(f"請先加入語音頻道！")
            return

        if not ctx.message.guild.voice_client:
            await join(ctx)

        global queue
        global now_playing

        if not ctx.message.guild.voice_client.is_playing():

            queue.append(url)

            video, source = search(queue.pop(0))

            now_playing = video["title"]

            async with ctx.typing():
                await ctx.send(f'**正在播放**：{video["title"]}')
                ctx.message.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source, executable="ffmpeg", **FFMPEG_OPTS), volume=0.1), after=lambda x: check_queue(ctx))

        else:

            queue.append(url)

            await ctx.send(f'**已加入撥放清單**：{search(url)[0]["title"]}')

    @commands.command(help="Format: !download <url> <playlist name>\nDownload music from url\n**BOT OWNER ONLY**")
    @commands.is_owner()
    async def download(self, ctx, url, playlist):
        #download music from url

        await YTDLSource.from_url(url, loop=self.bot.loop)

        #wirte audio filename into "{playlist}.txt"
        with open(f"{Root_Dir}/playlists/{playlist}.txt", 'a+') as f:

            f.seek(0)

            lines = [ s.rstrip('\n') for s in f.readlines() ]

            global filename
            filename = filename.lstrip(f"{Root_Dir}/audio files/")

            if filename not in lines:
                f.seek(2)
                f.write(filename + '\n')
                await ctx.send("**Done**")

            else:
                await ctx.send("**Already exists!**")

    @commands.command(help='Format: !play_local <playlist name>\nPlay local playlist\n**BOT OWNER ONLY**')
    @commands.is_owner()
    async def play_local(self, ctx, playlist=None):
        
        if playlist == None:
            await ctx.send("**You did not give a playlist!**")
            return

        if not ctx.message.author.voice:
            await ctx.send(f"請先加入語音頻道！")
            return

        if not ctx.message.guild.voice_client:
            await join(ctx)

        if not local_queue_init(playlist):
            await ctx.send("**Playlist not exist**")
            return
        
        await ctx.send(f'**Now playing playlist**: {playlist}')

        global local_queue

        audio = local_queue.pop(0)
        ctx.message.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="ffmpeg", source=f'{Root_Dir}/audio files/' + audio.rstrip('\n')), volume=0.1), after=lambda x: check_local_queue(ctx))

    @commands.command(help='shuffle queue')
    async def shuffle(self, ctx):
        if not queue and not local_queue:
            await ctx.send("no songs in queue!")
            return

        elif queue:
            shuffle(queue)
            
        elif local_queue:
            shuffle(local_queue)

        await ctx.send("queue shuffled!")

    @commands.command(help="Leaves the voice channel")
    async def leave(self, ctx):
        #Leave the voice channel

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()

        else:
            await ctx.send("沒有連接至任何語音頻道！")

    @commands.command(help='Clear the queue')
    async def clear(self, ctx):

        global queue
        queue.clear()
        local_queue.clear()

        async with ctx.typing():
            await ctx.send(f'**已清空播放清單**')

    @commands.command(help='View the queue')
    async def queue(self, ctx):
        if len(queue) < 1:
            await ctx.send('播放列表沒有音樂！')

        else:
            next = ''

            for url in queue:
                next += search(url)[0]["title"] + '\n'
            
            await ctx.send(f'{next}')

    @commands.command(help="Pause the music")
    async def pause(self, ctx):
        #Pause the music

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()

        else:
            await ctx.send("機器人沒有在播放音樂！")

    @commands.command(help="Resume the music")
    async def resume(self, ctx):
        #Resume the music

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        
        else:
            await ctx.send("之前沒有在播放音樂！使用**!play**來播放音樂")

    @commands.command(help="Stops the music")
    async def skip(self, ctx):
        #Skip the music

        global now_playing

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await ctx.send(f'**已跳過：**{now_playing}')
            voice_client.stop()
        
        else:
            await ctx.send("沒有在播放音樂！")

    @commands.command(help="Stops the music")
    async def stop(self, ctx):
        #Skip the music

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            queue.clear()
            local_queue.clear()
        
        else:
            await ctx.send("沒有在播放音樂！")

    @commands.command(name='now_playing', help='Show now playing song name')
    async def _now_playing(self, ctx):
        # Show now playing song name

        global now_playing

        if now_playing:
            async with ctx.typing():
                await ctx.send(f'**正在播放**：{now_playing}')

        else:
            await ctx.send('沒有在播放任何音樂！')


def setup(bot):
    bot.add_cog(Music(bot))