from discord.ext import commands
import discord
import json
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'config.json'),'r',encoding="utf8") as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix=jdata['prefix'], help_command=None)

@bot.event
async def on_ready():
    print('{0.user}起床囉'.format(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="支語殺"))
    
    print('Servers connected to:')
    for guild in bot.guilds:
        print(guild.name)

@bot.command(pass_context = True)
@commands.is_owner()
async def load(ctx, ext):
    await ctx.send(f'{ext} loaded')
    await bot.load_extension(f'cogs.{ext}')

@bot.command()
@commands.is_owner()
async def unload(ctx, ext):
    await ctx.send(f'{ext} unloaded')
    await bot.unload_extension(f'cogs.{ext}')

@bot.command()
@commands.is_owner()
async def reload(ctx, ext):
    await ctx.send(f'{ext} reloaded')
    await bot.reload_extension(f'cogs.{ext}') 

for filename in os.listdir(os.path.join(__location__, 'cogs')):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(jdata['token'])
