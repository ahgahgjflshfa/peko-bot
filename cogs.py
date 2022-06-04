import discord
from discord.ext import commands
import youtube_dl
from requests import get
from discord.errors import Forbidden

youtube_dl.utils.bug_reports_message = lambda: ''

# Global variables
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

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queue = []

now_playing = ''

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

async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)

# Discord commands
class Music(commands.Cog):
    """
    Contains music commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Stream from url')
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
                ctx.message.guild.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), volume=0.1), after=lambda x: check_queue(ctx))

        else:

            queue.append(url)

            await ctx.send(f'**已加入撥放清單**：{search(url)[0]["title"]}')

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

class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all modules of that bot"""
	
	    # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        prefix = '!'
        version = '1.0.0'

	    # setting owner name - if you don't wanna be mentioned remove line 49-60 and adjust help text (line 88) 
        owner = 448437774656471050
        owner_name = '蝦米碗糕#6182'

        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:
            # checks if owner is on this server - used to 'tag' owner
            try:
                owner = ctx.guild.get_member(owner).mention

            except AttributeError as e:
                owner = owner

            # starting to build embed
            emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{prefix}help <module>` to gain more information about that module '
                                            f':smiley:\n')

            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

            # setting information about author
            emb.add_field(name="About", value=f"壱百満天原サロメですわ～")
            emb.set_footer(text=f"Bot is running {version}")

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:

            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard from a module called `{input[0]}` before :scream:",
                                    color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module at once :sweat_smile:",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="It's a magical place.",
                                description="I don't know how you got here. But I didn't see this coming at all.\n"
                                            "Would you please be so kind to report that issue to me on github?\n"
                                            "https://github.com/nonchris/discord-fury/issues\n"
                                            "Thank you! ~Chris",
                                color=discord.Color.red())

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)


# Bot settings
intents = discord.Intents().all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents
)

def setup(bot):
    bot.add_cog(Music(bot))
    bot.add_cog(Help(bot))