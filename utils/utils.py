"""Utility functions for SVBot."""


async def reply(ctx, msg):
    """Send a message but also tag the user."""

    await ctx.send(
        f"{ctx.author.mention} " + msg
    )