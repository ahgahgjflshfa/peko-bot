from discord.ext import commands
from core.classes import Cog_Extension

class Event(Cog_Extension):
    """
    Eventですわ～
    """ 

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(987636041064263731)
        await channel.send(f"Welcome {member}!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(987636041064263731)
        await channel.send(f"{member} left!")

def setup(bot):
    bot.add_cog(Event(bot))