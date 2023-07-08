from __future__ import annotations

from typing import Dict, List, Any
import discord
from redbot.core import Config as Driver
from redbot.core import commands
import datetime
from redbot.core.bot import Red
from redbot.core.commands import Cog as Module

class Quarantine(Module):
    """Quarantine users in your server."""

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.driver: Driver = Driver.get_conf(self, identifier=123855555, force_registration=True)
        self.driver.register_member(roles=[])

    __author__ = "ellen.inator (`1103334703450308638`)"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad"""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nAuthor: {self.__author__}"

    @commands.bot_has_guild_permissions(manage_roles=True, moderate_members=True)
    @commands.bot_in_a_guild()
    @commands.command()
    @commands.mod()
    async def quarantine(self, ctx: commands.Context, *members: discord.Member) -> None:
        """Quarantine multiple users."""
        if not members:
            return await ctx.send_help(ctx.command)
        were_not_able: List[discord.Member] = []
        were_able: List[discord.Member] = []
        for member in members:
            if member.top_role >= ctx.guild.me.top_role:
                were_not_able.append(member)
                continue
            if member.is_timed_out():
                were_not_able.append(member)
                continue
            async with self.driver.member(member).all() as data:
                data["roles"] = [x.id for x in member.roles if x.is_assignable()]
            await member.remove_roles(
                *[x for x in member.roles if x.is_assignable()],
                reason=f"User got quarantined by: {str(ctx.author)}",
            )
            await member.timeout(
                datetime.timedelta(days=28),
                reason=f"User got quarantined by: {str(ctx.author)}",
            )
            were_able.append(member)
        to_send: str = ""
        if were_able:
            to_send += f"Quarantined {', '.join(str(x) for x in were_able)}. "
        if were_not_able:
            to_send += f"Couldn't quarantine {', '.join(str(x) for x in were_not_able)}."
        await ctx.send(to_send.strip())

    @commands.bot_has_guild_permissions(manage_roles=True, moderate_members=True)
    @commands.bot_in_a_guild()
    @commands.command()
    @commands.mod()
    async def unquarantine(self, ctx: commands.Context, *members: discord.Member) -> None:
        """Remove users from quarantine."""
        if not members:
            return await ctx.send_help(ctx.command)
        were_not_able: List[discord.Member] = []
        were_able: List[discord.Member] = []
        for member in members:
            if not member.is_timed_out():
                were_not_able.append(member)
                continue
            roles = (await self.driver.member(member).all()).get("roles", [])
            if not roles:
                were_not_able.append(member)
                continue
            roles = [ctx.guild.get_role(x) for x in roles]
            await member.add_roles(
                *[x for x in roles if x.is_assignable()],
                reason=f"User got unquarantined by: {str(ctx.author)}",
            )
            await member.timeout(None, reason=f"User got unquarantined by: {str(ctx.author)}")
            await self.driver.member(member).clear()
            were_able.append(member)
        to_send: str = ""
        if were_able:
            to_send += f"Unquarantined {', '.join(str(x) for x in were_able)}. "
        if were_not_able:
            to_send += f"Couldn't unquarantine {', '.join(str(x) for x in were_not_able)}."
        await ctx.send(to_send.strip())


async def setup(bot: Red):
    cog = Quarantine(bot)
    await bot.add_cog(cog)
