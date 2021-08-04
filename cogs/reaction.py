from discord.ext import commands
from zhconv import convert
import random
import time
import discord
import os
import jieba
import json

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

REACTIONS = [
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335866331295744/LmVdMYT.jpg',
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335866662649876/C_Chat.M.1595128807.A.E19.jpg',
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335869820940308/bx8C06k.png',
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335872639504414/iYBXvZg.jpg',
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335873646166046/iDLV0L8.jpg',
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335874396938290/Ja8PdF5.png',
    f'https://cdn.discordapp.com/attachments/870138830949322783/872335874971553828/7mLrCNah.jpg'
]


class reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        random.seed(int(time.time()))
        with open(os.path.join(__location__, "chinaword.txt"), "r", encoding='utf-8') as f:
            self.china_word = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, msg):
        messageContent = msg.content
        converted_message = convert(messageContent, 'zh-hant')
        seg_list = jieba.cut(converted_message)
        for seg in seg_list:
            if seg in self.china_word:
                await msg.add_reaction('<:zu2:815557862528122890>')
                author = msg.author.id
                if msg.author.bot:
                    break
                await msg.channel.send(f'<@{author}> 支語，滾！')
                mesg = random.choice(REACTIONS)
                await msg.channel.send(mesg)
                break

    @commands.command()
    async def update_word(self, ctx, arg = None):
        if not arg:
            await ctx.channel.send('usage: $update_word <zhi yu>')
            return
        if arg in self.china_word:
            await ctx.channel.send('親 這個支語已被收錄啦哈')
            return
        self.china_word.append(arg)
        await ctx.channel.send('親 已經為您更新支語資料庫啦哈')

    def __exit__(self):
        with open(os.path.join(__location__, 'chinaword.txt'), 'w', encoding='utf-8') as f:
            json.dump(self.china_word, f)


def setup(bot):
    bot.add_cog(reaction(bot))
