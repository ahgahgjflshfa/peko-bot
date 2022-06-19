from discord.ext import commands
from core.classes import Cog_Extension

class Welcome(Cog_Extension):
    """
    Welcome new member
    """ 

    def __init__(self, bot):
        self.bot = bot
        self.chid = None

    @commands.command(help='Set the channel to send welcome messages')
    @commands.is_owner()
    async def welcomeset(self, ctx):
        self.chid = ctx.message.channel.id

        await ctx.send("Channel Set", delete_after=10.0)

    @commands.command(help='Unset the channel to send welcome messages')
    @commands.is_owner()
    async def welcomeunset(self, ctx):
        self.chid = None

        await ctx.send("Channel Unset", delete_after=10.0)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.chid:
            channel = self.bot.get_channel(self.chid)
            await channel.send(f"Welcome {member}!")

    '''@commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(987636041064263731)
        await channel.send(f"{member} left!")'''

def setup(bot):
    bot.add_cog(Welcome(bot))