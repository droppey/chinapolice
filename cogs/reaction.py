# -*- coding: utf-8 -*-
from discord.ext import commands
from zhconv import convert
import random
import time
import discord
import os
import jieba
import json

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'reaction_setting.json'), 'r', encoding='utf-8') as setting_file:
    SETTINGS = json.load(setting_file)

class Reaction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        random.seed(int(time.time()))
        self.bot.ch = self.bot.get_channel(int(SETTINGS['id']))
        with open(os.path.join(__location__, 'chinaword.txt'), 'r', encoding='utf-8') as f:
            self.bot.china_word = [line[:-1] for line in f]
        with open(os.path.join(__location__, 'taiwanword.txt'), 'r', encoding='utf-8') as f:
            self.bot.taiwan_word = [line[:-1] for line in f]
        with open(os.path.join(__location__, 'mapping.json'), 'r', encoding='utf-8') as f:
            self.bot.c2t = json.load(f)
        jieba.load_userdict(os.path.join(__location__, 'chinaword.txt'))
        jieba.load_userdict(os.path.join(__location__, 'taiwanword.txt'))

    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.bot.get_context(msg)
        if ctx.valid :
            return
        messageContent = msg.content
        if 'https://' in messageContent or 'http://' in messageContent:
            return
        converted_message = convert(messageContent.lower(), 'zh-hant')
        seg_list = jieba.lcut(converted_message)

        for seg in seg_list:
            if seg in self.bot.china_word:
                if msg.author.bot:
                    return
                if seg in self.bot.c2t:
                    _tlist = jieba.lcut(converted_message.replace(seg, self.bot.c2t[seg]))
                    if len(_tlist) != len(seg_list):
                        continue
                await msg.add_reaction(SETTINGS['emoji'])
                author = msg.author.id
                await self.bot.ch.send(f'<@{author}> 支語，滾！')
                mesg = random.choice(SETTINGS['reaction_image'])
                await self.bot.ch.send(mesg)
                if seg in self.bot.c2t:
                  await self.bot.ch.send('同志好，您應該要說{}'.format(self.bot.c2t[seg]))
                return

    @commands.command()
    @commands.has_role(SETTINGS['maintainer_name'])
    async def bind_channel(self, ctx, arg=None):
        if arg:
            await ctx.channel.send('usage: $bind_channel')
            return
        self.bot.ch = ctx.channel
        await ctx.channel.send('綁定成功')

    @commands.command()
    @commands.has_role(SETTINGS['maintainer_name'])
    async def remove_word(self, ctx, arg=None):
        if not arg and len(arg) != 1:
            await ctx.channel.send('usage: $remove_word <fei zhi yu>')
            return
        arg = convert(arg.lower(), 'zh-hant')
        if arg not in self.bot.china_word:
            await ctx.channel.send('親 這個詞沒被誤認成支語啊 您佬再檢查一下唄')
            return
        self.bot.china_word.remove(arg)
        if arg in self.bot.c2t:
            self.bot.taiwan_word.remove(self.bot.c2t[arg])
            self.bot.c2t.pop(arg, None)
        await ctx.channel.send('親 已經為您更新支語數據庫啦哈 謝謝了哎')
        jieba.del_word(arg)

    @commands.command()
    @commands.has_role(SETTINGS['maintainer_name'])
    async def remove_taiwan_word(self, ctx, arg=None):
        if not arg and len(arg) != 1:
            await ctx.channel.send('usage: $remove_taiwan_word <fei tai wen>')
            return
        arg = convert(arg.lower(), 'zh-hant')
        if arg not in self.bot.taiwan_word:
            await ctx.channel.send('同志 這個詞彙並不在我台文詞庫中')
            return
        for c, t in self.bot.c2t.items():
            if t == arg:
              self.bot.c2t.pop(c, None)
        self.bot.taiwan_word.remove(arg)
        await ctx.channel.send('同志 謝謝你')
        jieba.del_word(arg)

    @commands.command()
    async def add_word(self, ctx, arg = None):
        if not arg and len(arg) != 1:
            await ctx.channel.send('usage: $add_word <zhi yu>')
            return
        arg = convert(arg.lower(), 'zh-hant')
        if arg in self.bot.china_word:
            await ctx.channel.send('親 這個支語已被收錄啦哈')
            return
        self.bot.china_word.append(arg)
        await ctx.channel.send('親 已經為您更新支語數據庫啦哈')
        jieba.add_word(arg)

    @commands.command()
    async def tag_word(self, ctx, *arg):
        if not arg or len(arg) != 2:
            await ctx.channel.send('usage: $add_word <zhi yu> <tai wen>')
            return
        arg_0 = convert(arg[0].lower(), 'zh-hant')
        arg_1 = convert(arg[1].lower(), 'zh-hant')
        if arg_0 not in self.bot.china_word:
            await ctx.channel.send('親 這個支語沒有被收錄呀 別瞎猜哎')
            return
        self.bot.c2t[arg_0] = arg_1
        if arg_1 not in self.bot.taiwan_word:
            self.bot.taiwan_word.append(arg_1)
            jieba.add_word(arg_1)
        await ctx.channel.send('親 已經為您更新支語數據庫啦哈')

def setup(bot):
    bot.add_cog(Reaction(bot))
