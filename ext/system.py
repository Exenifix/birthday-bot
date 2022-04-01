from datetime import datetime

import disnake
from disnake.ext import commands, tasks
from modules.bot import BdayBot


class SystemListeners(commands.Cog):
    def __init__(self, bot: BdayBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError
    ):
        if isinstance(error, commands.ConversionError):
            error = error.original
        await inter.send(
            embed=disnake.Embed(
                title="❌ | Error Occured", color=0xFF0000, description=str(error)
            ),
            ephemeral=True,
        )

        raise error


class SystemLoops(commands.Cog):
    def __init__(self, bot: BdayBot):
        self.bot = bot
        self.birthday_notifier.start()

    @tasks.loop(minutes=30)
    async def birthday_notifier(self):
        reset_day = await self.bot.get_reset()
        if reset_day > datetime.now().date():
            return

        await self.bot.update_reset()
        ids = await self.bot.get_birthdays_on_date()
        channel_ids = await self.bot.get_guild_ids()
        for guild in self.bot.guilds:
            if not guild.id in channel_ids or channel_ids[guild.id] is None:
                continue

            channel = guild.get_channel(channel_ids[guild.id])
            if channel is None:
                continue

            members = await guild.get_or_fetch_members(ids, cache=False)

            if len(members) == 0:
                continue

            elif len(members) > 30:
                members = members[:30]

            txt = "__**🎉 HAPPY BIRTHDAY TO THESE PERSONS 🎉**__\n"
            for member in members:
                txt += f"{member.mention}\n"

            await channel.send(txt)

    @birthday_notifier.before_loop
    async def loop_waiter(self):
        await self.bot.wait_until_ready()


def setup(bot: BdayBot):
    bot.add_cog(SystemListeners(bot))
    bot.add_cog(SystemLoops(bot))
