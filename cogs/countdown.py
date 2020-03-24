from discord.ext import commands
import discord, asyncio, aiohttp
import datetime, math, cogs.cmd_checks

class CountdownCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.countdown_check(True))

    def countdown_embed_creator(self, time_difference, countdown):
        date_days = math.floor(time_difference / 86400)
        time_difference -= (date_days * 86400)
        date_hours = math.floor(time_difference / 3600)
        time_difference -= (date_hours * 3600)                
        date_minutes = math.floor(time_difference / 60)
        time_difference -= (date_minutes * 60)
        date_seconds = math.floor(time_difference)

        embed = discord.Embed(title=f"Countdown to {countdown.name}", color=countdown.color)
        
        day_plural = "day" if date_days == 1 else "days"
        hour_plural = "hour" if date_hours == 1 else "hours"
        minute_plural = "minute" if date_minutes == 1 else "minutes"
        second_plural = "second" if date_seconds == 1 else "seconds"

        mess_value_1 = f"There are **{date_days} {day_plural}, {date_hours} {hour_plural}, {date_minutes} {minute_plural}, "
        mess_value_2 = f"and {date_seconds} {second_plural}** until {countdown.name}!"
        mess_value = mess_value_1 + mess_value_2

        embed.add_field(name="Time Till", value=mess_value)

        return embed

    @commands.command()
    @commands.check(cogs.cmd_checks.is_mod_or_up)
    async def forcerun_countdown(self, ctx):
        await self.countdown_check(False)
        await ctx.send("Done!")

    @commands.command()
    async def countdown(self, ctx, *, event_name):
        countdown_url = "https://raw.githubusercontent.com/Sonic4999/BappoRealmBot/master/countdowns.txt"
        event_list = []
        countdown = None

        async with aiohttp.ClientSession() as session:
            async with session.get(countdown_url) as resp:
                text = await resp.text()
                event_list = text.split("\n")

        for line in event_list:
            elements = line.split("|")

            if elements[0].lower() == event_name.lower():
                countdown = Countdown(elements[0], elements[1], elements[2], elements[3], elements[4])

        if countdown == None:
            await ctx.send(f"`{event_name}` is not a valid event. Check your spelling.")
        else:
            current_time = datetime.datetime.utcnow().timestamp()
            time_difference = countdown.time - current_time

            if (time_difference > 0):
                embed = self.countdown_embed_creator(time_difference, countdown)
                await ctx.send(embed=embed)

    async def countdown_check(self, loop):
        go = True

        while go:
            current_time = datetime.datetime.utcnow().timestamp()

            if loop == False:
                go = False
            else:
                multiplicity = math.ceil(current_time / 3600)
                next_one = multiplicity * 3600

                sleep_time = next_one - current_time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            countdown_url = "https://raw.githubusercontent.com/Sonic4999/BappoRealmBot/master/countdowns.txt"
            event_list = []
            countdown_list = []

            async with aiohttp.ClientSession() as session:
                async with session.get(countdown_url) as resp:
                    text = await resp.text()
                    event_list = text.split("\n")

            for line in event_list:
                elements = line.split("|")
                if len(elements) == 5:
                    countdown = Countdown(elements[0], elements[1], elements[2], elements[3], elements[4])
                    countdown_list.append(countdown)
                    print("Added Countdown!")

            for countdown in countdown_list:
                current_time = datetime.datetime.utcnow().timestamp()

                round_to_hour = math.floor(current_time / 100.0) * 100
                x_hour_factor = countdown.every_x_hours * 3600

                if round_to_hour == countdown.time:
                    embed = discord.Embed(title=f"Countdown to {countdown.name}", color=countdown.color)
                    embed.add_field(name="Time Till", value=f"**It's time for {countdown.name}!**")

                    channel = await self.bot.fetch_channel(countdown.channel_id)
                    await channel.send(embed=embed)
                    print("Done!")

                elif (round_to_hour % x_hour_factor) == 0:
                    time_difference = countdown.time - current_time

                    if (time_difference > 0):
                        embed = self.countdown_embed_creator(time_difference, countdown)
                        channel = await self.bot.fetch_channel(countdown.channel_id)
                        await channel.send(embed=embed)
                        print("Done!")


class Countdown():
    def __init__(self, name, color, channel_id, time, every_x_hours):
        self.name = name
        self.color = discord.Color(int(color, 0))
        self.channel_id = channel_id
        self.time = int(time)
        self.every_x_hours = int(every_x_hours)

def setup(bot):
    bot.add_cog(CountdownCMD(bot))