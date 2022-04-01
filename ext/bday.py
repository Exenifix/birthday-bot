import disnake
from disnake.ext import commands
from modules.bot import BdayBot
from modules.converters import Date, ShortDate


class BdayCommands(commands.Cog):
    def __init__(self, bot: BdayBot):
        self.bot = bot

    @commands.slash_command(name="setbday", description="Sets your birthday date.")
    async def setbday(self, inter: disnake.ApplicationCommandInteraction, date: Date):
        await self.bot.set_birthday(inter.author, date)
        await inter.send(f"✅ | Successfully set your birthday to **{date}**")

    @commands.slash_command(
        name="getbday", description="Gets a birthday of a user if they have set it up."
    )
    async def getbday(
        self, inter: disnake.ApplicationCommandInteraction, user: disnake.User
    ):
        bday = await self.bot.get_birthday(user)
        if bday is None:
            await inter.send("That user hasn't set their birthday yet!")
            return

        await inter.send(f"The birthday of {user.mention} is on **{bday}**!")

    @commands.slash_command(name="mybday", description="Shows your birthday.")
    async def mybday(self, inter: disnake.ApplicationCommandInteraction):
        bday = await self.bot.get_birthday(inter.author)
        if bday is None:
            await inter.send(
                "You don't have a birthday set up yet! Set it by using `/setbday` command!",
                ephemeral=True,
            )
            return

        await inter.send(f"Your birthday is on **{bday}**!")

    @commands.slash_command(
        name="birthdayson", description="Shows all birthdays on the set date."
    )
    async def birthdayson(
        self, inter: disnake.ApplicationCommandInteraction, date: ShortDate = None
    ):
        ids = await self.bot.get_birthdays_on_date(date)
        total_amount = len(ids)
        txt = ""

        members = await inter.guild.get_or_fetch_members(ids, cache=False)
        guild_wide_amount = len(members)
        if len(members) > 30:
            members = members[:30]

        for member in members:
            txt += f"{member}\n"

        if txt == "":
            txt = "No birthdays!"

        await inter.send(
            embed=disnake.Embed(
                title=f"Birthdays on {date.to_short_str()}",
                description=f"Total: **{total_amount}**\nOn this server: **{guild_wide_amount}**",
            ).add_field("Server members", txt)
        )

    @commands.slash_command(
        name="setbdaychannel", description="Sets a birthday channel."
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def setbirthdaychannel(
        self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel
    ):
        if not channel.permissions_for(inter.guild.me).send_messages:
            await inter.send("Bot cannot send messages in that channel!")
            return

        await self.bot.execute(
            "INSERT OR REPLACE INTO guilds (id, channel_id) VALUES (?, ?)",
            inter.guild.id,
            channel.id,
        )
        await inter.send(
            f"✅ | Successfully set the birthday channel to {channel.mention}!"
        )

    @commands.slash_command(
        name="resetbdaychannel", description="Resets the birthday channel."
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def resetbdaychannel(self, inter: disnake.ApplicationCommandInteraction):
        await self.bot.execute(
            "UPDATE guilds SET channel_id = NULL WHERE id = ?", inter.guild.id
        )
        await inter.send("✅ | Reset the birthday channel!")


def setup(bot: BdayBot):
    bot.add_cog(BdayCommands(bot))
