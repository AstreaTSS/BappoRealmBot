from discord.ext import commands
import discord, re, datetime

class GeneralCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help(self, ctx):

        embed = discord.Embed(colour=discord.Colour(0x4a90e2), description="A list of every command offered by this bot.")

        embed.set_author(name="Bappo Realm Custom Bot", icon_url="https://cdn.discordapp.com/avatars/618993974048194560/9533dc8ab73566f714731f17ed90d913.png")

        embed.add_field(name="Usable By Everyone", value="`help - Displays this.\nping - Pings the bot.\nsay <optional channel, message> - Makes the bot " +
        "say whatever you command it to. Can specify channel to send.\ncheck_stats <season> - Checks the stats for the season you give. Doesn't support the latest season.`\n")
        embed.add_field(name="Mod+ Commands", value="`season_add <season, a message id> - Gives the S<season> role (which must exist beforehand) to everyone " +
        "who joined before <a message id> was created.\nrole_id <role name> - Gets the ID of <role name>.\nverify <user> - Verifies the user mentioned.`")
        embed.add_field(name="Unstable Mod+ Commands", value="`forcerun_countdown - forceruns the countdown function\nforcerun_kick_unverified - forceruns the function " +
        "that kicks people who haven't been verified by 2 days of joining the server.`")

        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        current_time = datetime.datetime.utcnow().timestamp()
        mes_time = ctx.message.created_at.timestamp()

        ping_discord = round((self.bot.latency * 1000), 2)
        ping_personal = round((current_time - mes_time) * 1000, 2)

        await ctx.send(f"Pong! `{ping_discord}` ms from discord.\n`{ping_personal}` ms personally (not accurate)")

    @commands.command()
    async def say(self, ctx, *, message):

        args = message.split(" ")

        optional_channel = None

        if (re.search("[<#>]", args[0])):
            channel_id = re.sub("[<#>]", "", args[0])
            optional_channel = ctx.guild.get_channel(int(channel_id))
        if optional_channel is not None:
            await optional_channel.send(" ".join(args[1:]))
        else:
            await ctx.send(" ".join(args))

    @commands.command()
    async def check_stats(self, ctx, season):
        season_x_role = discord.utils.get(ctx.guild.roles, name=f'S{season}')
        if season_x_role == None:
            await ctx.send("Invalid season number!")
        else:
            count = 0
            list_of_people = []

            for member in ctx.guild.members:
                if season_x_role in member.roles:
                    count += 1
                    list_of_people.append(member.display_name)

            await ctx.send(f'There are {count} people that have the S{season} badge.')

            if len(list_of_people) > 90:
                n = 90
                split_of_people = [list_of_people[i * n:(i + 1) * n] for i in range((len(list_of_people) + n - 1) // n )]
                await ctx.author.send(f"```\nQuery of people in season {season}:\n```")

                for a_list in split_of_people:
                    mes_of_people = f"```\n"
                    for name in a_list:
                        mes_of_people += name + "\n"

                    await ctx.author.send(mes_of_people + "\n```")

            else:
                mes_of_people = f"```\nQuery about people in season {season}:\n"
                for name in list_of_people:
                    mes_of_people += name + "\n"

                await ctx.author.send(mes_of_people + "\n```")

def setup(bot):
    bot.add_cog(GeneralCMDS(bot))