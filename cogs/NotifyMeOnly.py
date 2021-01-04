"""DM me (and only me!) when a given user sends a message."""


from typing import Union
from datetime import datetime

from discord.abc import Messageable
from discord import Member, User

from discord.ext import commands
import discord


class NotifyMeOnly(commands.Cog):
    """DM me when a particular user sends a message."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.me = None

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if self.me is None:
            self.me = await self.bot.fetch_user(711994085480726639)

        if msg.author.display_name == 'theStudyVibes':
            await self.me.send("Alert! Alert!")

    @commands.Cog.listener()
    async def on_typing(self, channel: Messageable, user: Union[User, Member],
                        when: datetime):
        if self.me is None:
            self.me = await self.bot.fetch_user(711994085480726639)

        if user.display_name == 'theStudyVibes':
            await self.me.send("Alert!")


def setup(bot: commands.Bot):
    bot.add_cog(NotifyMeOnly(bot))