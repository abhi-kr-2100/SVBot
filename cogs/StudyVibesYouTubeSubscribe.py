"""Cog to get a DM when Study Vibes goes live."""


from os import getenv
from requests import get as http_get

import psycopg2

from discord.ext import commands, tasks

from .utils.utils import reply


class StudyVibesYouTubeSubscribe(commands.Cog):
    """Subscribe to get a DM whenever Study Vibes goes live."""

    def __init__(self, bot):
        self.bot = bot
        
        # ID of the video for which the most recent notification has been sent
        # this is used to prevent the bot from notifying for the same video
        # multiple times
        self.vid_id = None

        KEY = getenv('GOOGLE_API_KEY')
        self.api_call = (
            'https://youtube.googleapis.com/youtube/v3/search?part=id'
            '&channelId={}&eventType=live&maxResults=1&type=video&key={}'
        ).format('UCo4KXTfs6xXL5JvUIf3321A', KEY)
        
        self.subs_table = 'SVYTSubscription'

        self.conn = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
        self.cur  = self.conn.cursor()

        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.subs_table} (
                id          SERIAL PRIMARY KEY,
                member_id   BIGINT UNIQUE
            );
            """
        )
        self.conn.commit()

        self.notify.start()

    @commands.command(
        name='subscribe',
        help='Subscribe to receive a DM when Study Vibes goes live.'
    )
    async def subscribe(self, ctx):
        """Subscribe the author to receive a DM when Study Vibes goes live."""
        
        self.cur.execute(
            f'SELECT id FROM {self.subs_table} WHERE member_id = %s',
            (ctx.author.id,)
        )
        m = self.cur.fetchone()

        if m is not None:
            await reply(
                ctx,
                "You're already subscribed. To unsubscribe, use `!unsubscribe`."
            )
            return

        self.cur.execute(
            f'INSERT INTO {self.subs_table}(member_id) VALUES(%s)',
            (ctx.author.id,)
        )
        self.conn.commit()

        await reply(
            ctx,
            "You've been subscribed to receive a DM when Study Vibes goes live."
            " You can opt out of the subscription by using the `!unsubscribe`"
            " command."
        )

    @commands.command(
        name='unsubscribe',
        help="Stop receiving a DM when Study Vibes goes live."
    )
    async def unsubscribe(self, ctx):
        """End the subscription started by subscribe."""

        self.cur.execute(
            f'SELECT id FROM {self.subs_table} WHERE member_id = %s',
            (ctx.author.id,)
        )
        m = self.cur.fetchone()

        if m is None:
            await reply(
                ctx,
                "You are not subscribed. Please run `!subscribe` before "
                "`!unsubscribe` (😁)."
            )
            return

        self.cur.execute(
            f'DELETE FROM {self.subs_table} WHERE member_id = %s',
            (ctx.author.id,)
        )
        self.conn.commit()

        await reply(
            ctx,
            "You've been unsubscribed. You'll no longer receive a DM when "
            "Study Vibes goes live. If you've changed your mind, please run the"
            " `!subscribe` command."
        )

    @tasks.loop(minutes=1)
    async def notify(self):
        """Notify subscribed users when Study Vibes goes live."""

        if (upcoming := self._get_vid('upcoming')) is not None:
            await self._send_notifs(upcoming, False)
        elif (live := self._get_vid('live')) is not None:
            await self._send_notifs(live, True)

    def _get_vid(self, type):
        """
        Return the ID of an upcoming/live video on Study Vibes.
        
        If there are no such videos, return None.
        """

        API_CALL = self.api_call + f'&eventType={type}'

        resp = http_get(API_CALL)
        if resp.status_code != 200:
            return

        vids = resp.json()['items']
        return None if not vids else vids[0]['id']['videoId']

    async def _send_notifs(self, vid_id, live):
        """Send a DM to subscribers with the given video ID."""

        if self.vid_id == vid_id:
            # already notified for this video
            return
        else:
            self.vid_id = vid_id

        url = f'https://www.youtube.com/watch?v={vid_id}'
        if live:
            msg = f"Study Vibes just went live: {url}"
        else:
            msg = f"Study Vibes is about to go live: {url}"
        footer = (
            "If you would like to stop receiving these DMs, please use the "
            "`!unsubscribe` command."
        )

        subscribers = self.cur.execute(
            f'SELECT member_id FROM {self.subs_table}'
        ).fetchall()

        for u_id in subscribers:
            user = await self.bot.fetch_user(int(u_id[0]))
            await user.send(msg)
            await user.send(footer)


def setup(bot):
    bot.add_cog(StudyVibesYouTubeSubscribe(bot))