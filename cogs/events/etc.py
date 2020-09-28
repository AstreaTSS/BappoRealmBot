from discord.ext import commands
import discord, random
import cogs.utils as utils

class ETC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            gatekeeper = discord.utils.get(member.guild.roles, name='Gatekeeper')

            verify_channel = discord.utils.get(member.guild.channels, name='verify')
            gamertags = discord.utils.get(member.guild.channels, name='gamertags')

            verify_start = "".join((f"Welcome to the Bappo Realm, {member.mention}!\n\nYou might have ",
            "noticed that there's not a lot of channels. Well, that's because you have to be verified.\n\n",
            f"To get verified, **answer the below questions in this channel and put your gamertag in {gamertags.mention}.**\n",
            f"A {gatekeeper.mention} will then verify you, but this is a manual process, so it might take a while.\n\n"))

            verify_questions = "".join(("```\nVerification Questions:\n\n",
            "1. How did you come to know about this Realm? Don't just say 'advertising' if that's true " +
            "for you; be more specific, like stating from where.\n\n",
            "2. Roughly how long have you been playing Minecraft? If you've been playing Minecraft for a while, " +
            "what's your favorite part about Minecraft?\n\n",
            "3. Have you ever been a problem in Minecraft or Discord? If so, why?\n\n"
            "4. What platform/device(s) do you play on?\n\n",
            "5. Why did you join this Realm and what do you look forward to doing here?\n\n"
            "6. What is RULE 3 (not question 3) of this server?\n```"))

            await verify_channel.send(verify_start + verify_questions)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if type(channel) != discord.TextChannel:
            return

        if channel.category != None:
            if channel.category.id == 631591280979214346 and channel.name.startswith("ticket"):
                await channel.send(f"@everyone")

    @commands.Cog.listener()
    async def on_message(self, mes: discord.Message):
        if mes.guild == None:
            return
            
        rand_chance = random.randint(1, 4999)
        if rand_chance == 49:
            utils.msg_to_owner(self.bot, f"Added pineapple reaction to {mes.jump_url}")
            await mes.add_reaction("🍍")
def setup(bot):
    bot.add_cog(ETC(bot))
