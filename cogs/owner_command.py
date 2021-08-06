from discord.ext import commands
from discord import Embed

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension_name):
        if not extension_name:
            await ctx.send('usage: $load <name>')
        self.bot.load_extension(f'cogs.{extension_name}')

        await ctx.send(embed=Embed(title='load extension {}'.format(extension_name), description='成功'))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name):
        if not extension_name:
            await ctx.send('usage: $unload <name>')
        self.bot.unload_extension(f'cogs.{extension_name}')

        await ctx.send(embed=Embed(title='unload extension {}'.format(extension_name), description='成功'))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension_name):
        if not extension_name:
            await ctx.send('usage: $reload <name>')
        self.bot.reload_extension(f'cogs.{extension_name}')
        await ctx.send(embed=Embed(title='reload extension {}'.format(extension_name), description='成功'))

def setup(bot):
    bot.add_cog(OwnerCommands(bot))
