from discord.ext import commands
import discord
import json
import os
import logging

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class PoliceBot(commands.Bot):

    def __init__(self, log_mode='debug', log_file=False, filename='discord.log', *args, **kargs):
        super().__init__(*args, **kargs)
        self.logger = logging.getLogger('china_police')
        if log_mode == 'debug':
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        if log_file:
            handler = logging.FileHandler(filename=filename, encoding='utf-8', mode='w')
            handler.setLevel(logging.DEBUG)
        else:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)

        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self._was_ready_once = False

    async def on_ready(self):
        self.logger.info('{0.user}起床囉'.format(self))
        self.logger.info('Servers connected to:')
        for guild in self.guilds:
            self.logger.info(guild.name)
        if not self._was_ready_once:
            await self.on_first_ready()
            self._was_ready_once = True

    async def on_first_ready(self):
        for filename in os.listdir(os.path.join(__location__, 'cogs')):
            if filename.endswith('.py'):
                self.logger.info('載入 {} 模組'.format(filename[:-3]))
                self.load_extension(f'cogs.{filename[:-3]}')
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="支語殺"))

if __name__ == '__main__':
    with open(os.path.join(__location__, 'config.json'),'r',encoding="utf8") as jfile:
        jdata = json.load(jfile)
    bot = PoliceBot(command_prefix=jdata['prefix'], help_command=None)
    try:
        bot.run(jdata['token'])
    finally:
        if bot.china_word:
          with open(os.path.join(__location__, 'cogs', 'chinaword.txt'), 'w', encoding='utf-8') as f:
              f.write('\n'.join(bot.china_word))
              f.write('\n')
