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
        jieba.enable_parallel(4)
        with open(os.path.join(__location__, 'chinaword.txt'), 'r', encoding='utf-8') as f:
            self.bot.china_word = [line[:-1] for line in f]
        with open(os.path.join(__location__, 'taiwanword.txt'), 'r', encoding='utf-8') as f:
            self.bot.taiwan_word = [line[:-1] for line in f]
        with open(os.path.join(__location__, 'mapping.json'), 'r', encoding='utf-8') as f:
            self.bot.c2t = json.load(f)
        jieba.load_userdict(os.path.join(__location__, 'chinaword.txt'))
        for word in self.bot.china_word:
            if word.isnumeric():
                jieba.del_word(word)


    @commands.Cog.listener()
    async def on_message(self, msg):
        ctx = await self.bot.get_context(msg)
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
                    if _tlist[i][1] != start or _tlist[i][2] != end:
                        continue
                await msg.add_reaction(SETTINGS['emoji'])
                await self.bot.ch.send('支語，滾！')
                mesg = random.choice(SETTINGS['reaction_image'])
                await self.bot.ch.send(mesg)
                if seg in self.bot.c2t:
                    await self.bot.ch.send('同志好，您應該要說{}'.format(self.bot.c2t[seg]))
                return

    @commands.command()
    @commands.has_role(SETTINGS['maintainer_name'])
    async def bind_channel(self, ctx, arg):
        if arg:
            await ctx.channel.send('usage: $bind_channel')
            return
        self.bot.ch = ctx.channel
        await ctx.channel.send('綁定成功')

    @commands.command()
    @commands.has_role(SETTINGS['maintainer_name'])
    async def remove_word(self, ctx, *arg):
        if not arg or len(arg) != 1:
            await ctx.channel.send('usage: $remove_word <fei zhi yu>')
            return
        arg = arg[0]
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
    async def remove_taiwan_word(self, ctx, *arg):
        if not arg or len(arg) != 1:
            await ctx.channel.send('usage: $remove_taiwan_word <fei tai wen>')
            return
        arg = arg[0]
        arg = convert(arg.lower(), 'zh-hant')
        if not arg in self.bot.taiwan_word:
            await ctx.channel.send('同志 這個詞彙並不在我台文詞庫中')
            return
        for c, t in self.bot.c2t.items():
            if t == arg:
              self.bot.c2t.pop(c, None)
              break
        self.bot.taiwan_word.remove(arg)
        await ctx.channel.send('同志 謝謝你')
        jieba.del_word(arg)

    @commands.command()
    async def add_word(self, ctx, *args):
        if not args:
            await ctx.channel.send('usage: $add_word <zhi yu> ...')
            return
        if len(args) > 1:
            msg = '親 這個支語已被收錄啦哈'
        else:
            msg = '親 其中一個'
        appended = False
        for arg in args:
            arg = convert(arg.lower(), 'zh-hant')
            if arg in self.bot.china_word:
                if len(args) == 1:
                    await ctx.channel.send('親 這個支語已被收錄啦哈')
                else:
                    await ctx.channel.send('親 謹查{}已被收錄於數據庫中'.format(arg))
                continue
            appended = True
            self.bot.china_word.append(arg)
            jieba.add_word(arg)
        if appended:
            await ctx.channel.send('親 已經為您更新支語數據庫啦哈')

    @commands.command()
    async def tag_word(self, ctx, *args):
        if not args or len(args) != 2:
            await ctx.channel.send('usage: $tag_word <zhi yu> <tai wen>')
            return
        arg_0 = convert(args[0].lower(), 'zh-hant')
        arg_1 = convert(args[1].lower(), 'zh-hant')
        if not arg_0 in self.bot.china_word:
            await ctx.channel.send('親 這個支語沒有被收錄呀 別瞎猜哎')
            returnf
        self.bot.c2t[arg_0] = arg_1
        if not arg_1 in self.bot.taiwan_word:
            self.bot.taiwan_word.append(arg_1)
        await ctx.channel.send('親 已經為您更新支語數據庫啦哈')

def setup(bot):
    bot.add_cog(Reaction(bot))
