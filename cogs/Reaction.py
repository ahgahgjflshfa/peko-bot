import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json
import os

Root_Dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

class Reaction(Cog_Extension):
    """
    Give role to member who react to specific message
    """

    @commands.command(help='!rrset <emoji> <role>\nSet emoji reaction with a role')
    async def rrset(self, ctx, emoji, role: discord.Role):
        with open(f'{Root_Dir}/config/ReactRole.json') as json_file:
            data = json.load(json_file)

            new_react_role = {
                'role_name': role.name, 
                'role_id': role.id,
                'emoji': emoji
            }

            if str(ctx.guild.id) not in data:
                data[ctx.guild.id] = [new_react_role]

            elif new_react_role not in data[str(ctx.guild.id)]:
                for info in data[str(ctx.guild.id)]:
                    if info["role_id"] == role.id:
                        #判斷這個身分組是否已設定
                        await ctx.send("Role already assigned!", delete_after=5.0)
                        return
                    
                    elif info["emoji"] == emoji:
                        #判斷這個貼圖是否已設定
                        await ctx.send("Emoji already used!", delete_after=5.0)
                        return

                    else:
                        data[str(ctx.guild.id)].append(new_react_role)
                        break

            else:
                await ctx.send("**Already Exist!**")
                return
            

        with open(f'{Root_Dir}/config/reactrole.json', 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send("Set")

    @commands.command(help="!rrmessage\nSend message listened by the bot for getting roles")
    async def rrmessage(self, ctx):
        with open(f'{Root_Dir}/config/ReactRole.json') as json_file:
            data = json.load(json_file)

            if str(ctx.guild.id) not in data:
                await ctx.send("Did not setup anythong yet!\nUse `!rset <emoji> <role> <description>` to set up.")
                return
            
            # message content
            embed = discord.Embed(title='Get Role', color=0xff0000)
            emoji = []
            description = ''
            for info in data[str(ctx.guild.id)]:
                description += f'{info["emoji"]} | <@&{str(info["role_id"])}>\n'
                emoji.append(info["emoji"])

            embed.description = description
            msg = await ctx.send(embed=embed)

            for e in emoji:
                await msg.add_reaction(e)

        with open(f'{Root_Dir}/config/MessageID.json') as mid:
            data = json.load(mid)

            data[str(ctx.guild.id)] = msg.id

        with open(f'{Root_Dir}/config/MessageID.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command(help='No arguments\nClear all the settings')
    async def rrclear(self, ctx):
        with open(f'{Root_Dir}/config/ReactRole.json') as json_file:
            data = json.load(json_file)

            del data[str(ctx.guild.id)]

        with open(f'{Root_Dir}/config/ReactRole.json', 'w') as f:
            json.dump(data, f, indent=4)

        with open(f'{Root_Dir}/config/MessageID.json') as json_file:
            data = json.load(json_file)

            del data[str(ctx.guild.id)]

        with open(f'{Root_Dir}/config/MessageID.json', 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send('Setting cleared', delete_after=5.0)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            pass

        else:
            with open(f'{Root_Dir}/config/MessageID.json') as f:
                data = json.load(f)
                if str(payload.guild_id) not in data:
                    return
                
                if not payload.message_id == data[str(payload.guild_id)]:
                    return

            with open(f'{Root_Dir}/config/ReactRole.json') as json_file:
                data = json.load(json_file)

                for info in data[str(payload.guild_id)]:
                    if info["emoji"] == payload.emoji.name:
                        role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=info["role_id"])

                        await payload.member.add_roles(role)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        with open(f'{Root_Dir}/config/MessageID.json') as f:
            data = json.load(f)
            if str(payload.guild_id) not in data:
                return
            
            if not payload.message_id == data[str(payload.guild_id)]:
                return

        with open(f'{Root_Dir}/config/ReactRole.json') as json_file:
            data = json.load(json_file)

            for info in data[str(payload.guild_id)]:
                if info["emoji"] == payload.emoji.name:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=info["role_id"])

                    await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)
            

def setup(bot):
    bot.add_cog(Reaction(bot))
