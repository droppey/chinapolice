# -*- coding: utf-8 -*-
from discord.ext import commands
from discord import Embed
from zhconv import convert
import random
import time
import discord
import os
import jieba
import json
import time

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'reaction_setting.json'), 'r', encoding='utf-8') as setting_file:
    SETTINGS = json.load(setting_file)


def guild_compare():
    async def guild_filter(ctx):
        return str(ctx.guild.id) == SETTINGS['guild']
    return commands.check(guild_filter)

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        random.seed(int(time.time()))
        self.bot.guilds_dict = {}
        if os.path.exists(os.path.join(__location__, SETTINGS['self_dictionary'])):
            jieba.initialize()
            jieba.set_dictionary(os.path.join(__location__, SETTINGS['self_dictionary']))
        jieba.enable_parallel(3)
        for guild in self.bot.guilds:
            self.bot.guilds_dict[str(guild.id)] = {'ch': '', 'emoji': ''}
        with open(os.path.join(__location__, 'server_mapping.json'), 'r', encoding='utf-8') as f:
            svr_mapping = json.load(f)
            for guild_id, mapping in svr_mapping.items():
                if guild_id in self.bot.guilds_dict:
                    self.bot.guilds_dict[guild_id]['ch'] = self.bot.get_channel(int(mapping['cid'])) if mapping['cid'].isnumeric() else None
                    self.bot.guilds_dict[guild_id]['emoji'] = mapping['emoji']
            self.bot.svr_mapping = {guild_id:svr_mapping[guild_id] for guild_id in svr_mapping.keys() if guild_id in self.bot.guilds_dict}
        for guild in self.bot.guilds:
            if not str(guild.id) in self.bot.svr_mapping:
                self.bot.svr_mapping[str(guild.id)] = {'cid': '', 'emoji': ''}
        with open(os.path.join(__location__, 'chinaword.txt'), 'r', encoding='utf-8') as f:
            self.bot.china_word = [line[:-1] for line in f]
        with open(os.path.join(__location__, 'taiwanword.txt'), 'r', encoding='utf-8') as f:
            self.bot.taiwan_word = [line[:-1] for line in f]
        with open(os.path.join(__location__, 'mapping.json'), 'r', encoding='utf-8') as f:
            self.bot.c2t = json.load(f)
        jieba.load_userdict(os.path.join(__location__, 'chinaword.txt'))
        for word in self.bot.china_word:
            if word.isnumeric() or word.isascii():
                jieba.del_word(word)
        self.listeners = {}

    def add_listener(self, event, listener):
        if event not in self.listeners:
            self.listeners[event] = [listener]
        else:
            self.listeners[event].append(listener)

    def remove_all_listener(self, event):
        self.listeners[event] = []

    def remove_listener(self, event, listener):
        if event not in self.listeners:
            return

        self.listeners[event].remove(listener)

    async def _emit(self, event, *args):
        if event not in self.listeners:
            return

        for listener in self.listeners[event]:
            if callable(listener):
                await listener(*args)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            await self._emit('remove_word_voting', reaction)
        except Exception as ex:
            self.bot.logger.info(f'remove_word_voting fails due to {ex} \n and start to remove listener')
            self.remove_all_listener('remove_word_voting')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.svr_mapping[str(guild.id)] = {'cid': '', 'emoji': ''}
        self.bot.guilds_dict[str(guild.id)] = {'ch': '', 'emoji': ''}
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            await guild.system_channel.send('00???????????????{}???????????????????????????`-bind_reaction <????????????>`??????emoji????????????????????????`-bind_channel`????????????'.format(self.bot.user))
        self.bot.logger.info(f'????????? {guild.name} ??????')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        del self.bot.svr_mapping[str(guild.id)]
        del self.bot.guilds_dict[str(guild.id)]
        self.bot.logger.info(f'????????? {guild.name} ??????')

    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.bot.get_context(msg)
        guild_id = ctx.guild.id
        if ctx.valid :
            return
        messageContent = msg.content
        if 'https://' in messageContent or 'http://' in messageContent:
            return
        converted_message = convert(messageContent.lower(), 'zh-hant')
        seg_list = list(jieba.tokenize(converted_message))
        for i, (seg, start, end) in enumerate(seg_list):
            if seg in self.bot.china_word:
                if msg.author.bot:
                    return
                if seg in self.bot.c2t:
                    _tlist = list(jieba.tokenize(converted_message.replace(seg, self.bot.c2t[seg])))
                    if len(_tlist) != len(seg_list) + len(jieba.lcut(self.bot.c2t[seg])) -1:
                        continue
                    if _tlist[i][1] != start:
                        continue
                await msg.add_reaction(self.bot.guilds_dict[str(guild_id)]['emoji'])
                if 'ch' in self.bot.guilds_dict[str(guild_id)]:
                    try:
                        await self.bot.guilds_dict[str(guild_id)]['ch'].send('???????????????')
                        mesg = random.choice(SETTINGS['reaction_image'])
                        await self.bot.guilds_dict[str(guild_id)]['ch'].send(mesg)
                        if seg in self.bot.c2t:
                            await self.bot.guilds_dict[str(guild_id)]['ch'].send('???????????????????????????{}'.format(self.bot.c2t[seg]))
                    except AttributeError as e:
                        self.bot.logger.info(f'send message abort possibly due to missing channel or emoji where is {e}')
                return

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def bind_reaction(self, ctx, *arg):
        if not arg or len(arg) != 1:
            await ctx.channel.send('usage example: $bind_reaction ????')
            return
        arg = arg[0]
        self.bot.guilds_dict[str(ctx.guild.id)]['emoji'] = arg
        self.bot.svr_mapping[str(ctx.guild.id)]['emoji'] = arg
        await ctx.channel.send('??????emoji????????????')

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def bind_channel(self, ctx, *arg):
        if arg:
            await ctx.channel.send('usage: $bind_channel')
            return
        self.bot.guilds_dict[str(ctx.guild.id)]['ch'] = ctx.channel
        self.bot.svr_mapping[str(ctx.guild.id)]['cid'] = str(ctx.channel.id)
        await ctx.channel.send('????????????')

    @guild_compare()
    @commands.command()
    async def remove_word(self, ctx, *arg):
        if not arg or len(arg) != 1:
            await ctx.channel.send('usage: $remove_word <fei zhi yu>')
            return
        arg = arg[0]
        arg = convert(arg.lower(), 'zh-hant')
        if arg not in self.bot.china_word:
            await ctx.channel.send('??? ????????????????????????????????? ????????????????????????')
            return
        if not ctx.message.author.guild_permissions.manage_roles:
            msg = await ctx.channel.send(embed=Embed(title=f'?????????????????? ???????????? {arg} ????????????',
                        description='???????????? ?????????????????? ??????????'))
            await msg.add_reaction('????')
            def _remove_word_voting(last_time):
                async def _inner(reaction):
                    nonlocal last_time
                    now_time = time.time()
                    if now_time - last_time > 600:
                        self.remove_listener('remove_word_voting', _inner)
                    if reaction.message.id != msg.id:
                        return
                    if reaction.count >= 6 and str(reaction.emoji) == '????':
                        self.bot.china_word.remove(arg)
                        if arg in self.bot.c2t:
                            self.bot.taiwan_word.remove(self.bot.c2t[arg])
                            self.bot.c2t.pop(arg, None)
                        await ctx.channel.send('??? ??????????????????????????????????????? ????????????')
                        jieba.del_word(arg)
                        self.remove_listener('remove_word_voting', _inner)
                return _inner

            self.add_listener('remove_word_voting', _remove_word_voting(time.time()))
        else:
            self.bot.china_word.remove(arg)
            if arg in self.bot.c2t:
                self.bot.taiwan_word.remove(self.bot.c2t[arg])
                self.bot.c2t.pop(arg, None)
            await ctx.channel.send('??? ??????????????????????????????????????? ????????????')
            jieba.del_word(arg)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @guild_compare()
    async def remove_taiwan_word(self, ctx, *arg):
        if not arg or len(arg) != 1:
            await ctx.channel.send('usage: $remove_taiwan_word <fei tai wen>')
            return
        arg = arg[0]
        arg = convert(arg.lower(), 'zh-hant')
        if not arg in self.bot.taiwan_word:
            await ctx.channel.send('?????? ???????????????????????????????????????')
            return
        for c, t in self.bot.c2t.items():
            if t == arg:
              self.bot.c2t.pop(c, None)
              break
        self.bot.taiwan_word.remove(arg)
        await ctx.channel.send('?????? ?????????')
        jieba.del_word(arg)

    @guild_compare()
    @commands.command()
    async def add_word(self, ctx, *args):
        if not args:
            await ctx.channel.send('usage: $add_word <zhi yu> ...')
            return
        appended = False
        for arg in args:
            arg = convert(arg.lower(), 'zh-hant')
            if arg in self.bot.china_word:
                if len(args) == 1:
                    await ctx.channel.send('??? ??????????????????????????????')
                else:
                    await ctx.channel.send('??? ??????{}???????????????????????????'.format(arg))
                continue
            appended = True
            self.bot.china_word.append(arg)
            if not arg.isascii():
                jieba.add_word(arg)
        if appended:
            await ctx.channel.send('??? ???????????????????????????????????????')


    @guild_compare()
    @commands.command()
    async def tag_word(self, ctx, *args):
        if not args or len(args) != 2:
            await ctx.channel.send('usage: $tag_word <zhi yu> <tai wen>')
            return
        arg_0 = convert(args[0].lower(), 'zh-hant')
        arg_1 = convert(args[1].lower(), 'zh-hant')
        if not arg_0 in self.bot.china_word:
            await ctx.channel.send('??? ?????????????????????????????? ????????????')
            return
        self.bot.c2t[arg_0] = arg_1
        if not arg_1 in self.bot.taiwan_word:
            self.bot.taiwan_word.append(arg_1)
        await ctx.channel.send('??? ???????????????????????????????????????')

def setup(bot):
    bot.add_cog(Reaction(bot))
