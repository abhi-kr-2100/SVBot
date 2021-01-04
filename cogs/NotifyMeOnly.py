"""DM me (and only me!) when a given user sends a message."""


from typing import Union
from datetime import datetime

from discord.abc import Messageable
from discord import Member, User, Message, TextChannel

from discord.ext import commands


class NotifyMeOnly(commands.Cog):
    """DM me when a particular user sends a message."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.my_id = 711994085480726639
        self.me = None

        self.targets = ['theStudyVibes']

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        if self.me is None:
            self.me = await self.bot.fetch_user(self.my_id)

        if (name := msg.author.display_name) in self.targets:
            await self.me.send(f"{name} sent a message: {msg.jump_url}.")

    @commands.Cog.listener()
    async def on_typing(self, channel: Messageable, user: Union[User, Member],
                        when: datetime):
        if self.me is None:
            self.me = await self.bot.fetch_user(self.my_id)

        if (name := user.display_name) in self.targets:
            msg = f"{name} is typing"
            if isinstance(channel, TextChannel):
                msg += f" in {channel.mention}"
            msg += "."

            await self.me.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(NotifyMeOnly(bot))