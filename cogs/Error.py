from discord.ext import commands
from cogs.Music import Music
from core.classes import Cog_Extension

class Error(Cog_Extension):
    """
    Error Handler
    """

    #其他的Error Handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        #檢查指令有沒有自己的錯誤處理
        if hasattr(ctx.command, 'on_error'):
            return 

        await ctx.send(error)

    # 個別指令的Error Handler
'''    @Music.play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("**Missing url**")'''

def setup(bot):
    bot.add_cog(Error(bot))