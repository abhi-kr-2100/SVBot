"""
A Cog to display the next Study Vibes livestream in the given country's
timezone.
"""


from os import getenv

from datetime import datetime

from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError

import psycopg2

from requests import get as http_get

from discord.ext import commands

from .utils.utils import reply


class NextLiveStreamCog(commands.Cog):
    """Cog to display the next stream's time in a given country's timezone."""

    def __init__(self, bot):
        self.bot = bot

        self.timezones = self._get_timezones()
        self.time_format = "%B %d at %I:%M %P"

        self.tz_table = 'timezones'

        conn = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
        cur = conn.cursor()

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.tz_table} (
                id              SERIAL PRIMARY KEY,
                member_id       BIGINT UNIQUE,
                timezone_name   TEXT
            );
            """
        )
        conn.commit()

        cur.close()
        conn.close()

    @commands.command(
        name='tzset',
        help='Set a particular timezone for yourself.'
    )
    async def tzset(self, ctx: commands.Context, tz_name: str) -> None:
        """Save the given timezone for the user who calls this command."""

        user_id = ctx.author.id
        try:
            tz = timezone(tz_name)
        except UnknownTimeZoneError:
            await reply(
                ctx,
                f"{tz_name} is not a valid timezone name. A valid timezone name"
                " looks like this: Europe/Brussels. You can find the correct "
                "timezone for your country/city here: "
                "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            )
            return

        conn = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
        cur = conn.cursor()

        cur.execute(
            f"""
            INSERT INTO {self.tz_table} (member_id, timezone_name)
            VALUES (%s, %s)
            ON CONFLICT (member_id)
            DO
                UPDATE SET timezone_name = EXCLUDED.timezone_name;
            """,

            (user_id, tz_name)
        )
        conn.commit()

        cur.close()
        conn.close()

        await reply(ctx, f"You've successfully set your timezone to {tz_name}")

    @commands.command(
        name='nextls',
        help="Display next livestream in country's timezone."
    )
    async def nextls(self, ctx, country=None):
        """
        Display when the next stream is in given country's timezone.
        
        If no country is given, display in Heleen's timezone.
        """

        if country is None:
            conn = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
            cur = conn.cursor()

            cur.execute(
                f"""
                SELECT timezone_name FROM {self.tz_table}
                    WHERE member_id = %s;
                """,
                (ctx.author.id,)
            )
            result = cur.fetchone()
            country = 'Heleen' if result is None else result[0]

        if '/' not in country:
            country = country.lower()

            if country not in self.timezones:
                await reply(
                    ctx,
                    f"TZ data for {country} is not available yet. "
                    "You can request the mods to add TZ data for your country."
                )
                return
            tzname = self.timezones[country]
        else:
            tzname = country

        try:
            tz = timezone(tzname)
        except UnknownTimeZoneError:
            await reply(
                ctx,
                f"'{tzname}' is not a valid timezone."
            )
            return

        try:
            stream_time = self._get_future_livestream()
        except ValueError:
            await reply(
                ctx,
                "No upcoming streams found. Wait for the study calendar to "
                "be updated. This may take a few days."
            )
            return
        except ConnectionError as ex:
            await reply(
                ctx,
                str(ex) + " This shouldn't have happened. "
                "Please note the status code and inform the mods."
            )
            return

        start_time = stream_time.astimezone(tz)

        if start_time <= datetime.now().astimezone(tz):
            msg = ("There is a livestream going on now! "
                   "Check out the Study Vibes YouTube channel.")
        else:
            msg = ("The next livestream is on "
                  f"{start_time.strftime(self.time_format)}")
            if country != 'Heleen'.lower():
                msg += f" (time according to {tzname})"
            else:
                msg += " (Heleen's original time)"

        await reply(ctx, msg)

    
    def _get_future_livestream(self):
        """Return the time for the next livestream."""

        API_KEY     = getenv('GOOGLE_API_KEY')
        HELEEN_TZ   = timezone(self.timezones['Heleen'.lower()])
        CALENDAR_ID = 'oro5litmqb6972jgi5bgp4dg4k@group.calendar.google.com'
        API_CALL    = (
            'https://www.googleapis.com/calendar/v3/calendars/{}/events?'
            'maxResults=1&singleEvents=true&timeMin={}&key={}&orderBy=startTime'
        )

        now = datetime.now().astimezone(HELEEN_TZ)
        
        # look only for those livestreams that are to end after time_min
        # special characters must be replaced by URL-friendly codes
        time_min = now.isoformat().replace(':', '%3A').replace('+', '%2B')

        resp = http_get(API_CALL.format(CALENDAR_ID, time_min, API_KEY))
        if resp.status_code != 200:
            raise ConnectionError(
                f"GET failed. Status code: {resp.status_code}."
            )

        events = resp.json()['items']
        if not events:
            raise ValueError("No upcoming events.")

        return datetime.fromisoformat(events[0]['start']['dateTime'])

    
    def _get_timezones(self):
        """Return a dictionary mapping country with timezone."""

        TZ_FILENAME = getenv('TZ_FILENAME')

        with open(TZ_FILENAME) as tzf:
            return dict(
                (t[0].lower(), t[1]) for t in [line.split() for line in tzf]
            )


def setup(bot):
    bot.add_cog(NextLiveStreamCog(bot))