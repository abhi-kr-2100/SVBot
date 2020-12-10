"""A modular and extensible Discord bot."""


from os import getenv, environ, listdir

from discord.ext.commands import Bot


if not 'RUNNING_ON_HEROKU' in environ:
    from dotenv import load_dotenv
    load_dotenv()


TOKEN = getenv('DISCORD_TOKEN')
CMD_PREFIX = getenv('DISCORD_CMD_PREFIX')

COG_FILE_EXT = '.py'


bot = Bot(command_prefix=CMD_PREFIX)

for filename in listdir('cogs'):
    if filename.endswith(COG_FILE_EXT):
        cog_name = filename[:-len(COG_FILE_EXT)]
        bot.load_extension(f'cogs.{cog_name}')

bot.run(TOKEN)