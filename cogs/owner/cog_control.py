#!/usr/bin/env python3.7
from discord.ext import commands
import discord, datetime, asyncio, traceback
from pathlib import Path

async def error_handle(bot, error, ctx = None):
    error_str = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
    await msg_to_owner(bot, error_str)

    if ctx != None:
        await ctx.send("An internal error has occured. The owner of the bot has been notified.")

async def msg_to_owner(bot, string):
    application = await bot.application_info()
    owner = application.owner
    await owner.send(f"{string}")

def file_to_ext(str_path, start_path):
    str_path = str_path.replace(start_path, "")
    str_path = str_path.replace("/", ".")
    return str_path.replace(".py", "")

def get_all_extensions(filename):
    ext_files = []
    loc_split = filename.split("cogs")
    start_path = loc_split[0]

    if start_path == filename:
        start_path = start_path.replace("main.py", "")
    start_path = start_path.replace("\\", "/")

    pathlist = Path(f"{start_path}/cogs").glob('**/*.py')
    for path in pathlist:
        str_path = str(path.as_posix())
        str_path = file_to_ext(str_path, start_path)

        ext_files.append(str_path)

    return ext_files

class CogControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def msg_handler(self, ctx, msg_str):
        await ctx.send(msg_str)

        utcnow = datetime.datetime.utcnow()
        time_format = utcnow.strftime("%x %X UTC")

        await msg_to_owner(ctx.bot, f"`{time_format}`: {msg_str}")

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def load_extension(self, ctx, extension):
        try:
            self.bot.load_extension(extension)
        except commands.ExtensionNotFound:
            return await ctx.send(f"Extension '{extension}' not found!")
        except commands.ExtensionAlreadyLoaded:
            return await ctx.send(f"Extension '{extension}' already loaded!")
        except commands.NoEntryPointError:
            return await ctx.send(f"There was no entry point for '{extension}'!")
        except commands.ExtensionFailed:
            raise

        await self.msg_handler(ctx, f"Extension '{extension}' loaded!")

    @commands.command()
    async def reload_extension(self, ctx, extension):
        try:
            self.bot.reload_extension(extension)
        except commands.ExtensionNotFound:
            return await ctx.send(f"Extension '{extension}' not found!")
        except commands.ExtensionNotLoaded:
            return await ctx.send(f"Extension '{extension}' not loaded!")
        except commands.NoEntryPointError:
            return await ctx.send(f"There was no entry point for '{extension}'!")
        except commands.ExtensionFailed:
            raise

        await self.msg_handler(ctx, f"Extension '{extension}' reloaded!")

    @commands.command()
    async def unload_extension(self, ctx, extension):
        try:
            self.bot.unload_extension(extension)
        except commands.ExtensionNotLoaded:
            return await ctx.send(f"Extension '{extension}' is not loaded!'")

        await self.msg_handler(ctx, f"Extension '{extension}' unloaded!")

    @commands.command()
    async def reload_all_extensions(self, ctx):
        for extension in self.bot.extensions.keys():
            self.bot.reload_extension(extension)

        await self.msg_handler(ctx, f"All extensions reloaded!")

    @commands.command()
    async def refresh_extensions(self, ctx):
        def ext_str(list_files):
            exten_list = [f"`{k}`" for k in list_files]
            return ", ".join(exten_list)

        unloaded_files = []
        reloaded_files = []
        loaded_files = []

        ext_files = get_all_extensions(__file__)

        to_unload = [e for e in self.bot.extensions.keys() 
        if e not in ext_files]
        for ext in to_unload:
            self.bot.unload_extension(ext)
            unloaded_files.append(ext)
        
        for ext in ext_files:
            try:
                self.bot.reload_extension(ext)
                reloaded_files.append(ext)
            except commands.ExtensionNotLoaded:
                self.bot.load_extension(ext)
                loaded_files.append(ext)
            except commands.ExtensionNotFound as e:
                await error_handle(self.bot, e)
            except commands.NoEntryPointError:
                pass
            except commands.ExtensionFailed as e:
                await error_handle(self.bot, e)

        msg_content = ""

        if unloaded_files != []:
            msg_content += f"Unloaded: {ext_str(unloaded_files)}\n"
        if loaded_files != []:
            msg_content += f"Loaded: {ext_str(loaded_files)}\n"
        if reloaded_files != []:
            msg_content += f"Reloaded: {ext_str(reloaded_files)}\n"

        await self.msg_handler(ctx, msg_content)

    @commands.command()
    async def list_loaded_extensions(self, ctx):
        exten_list = [f"`{k}`" for k in self.bot.extensions.keys()]
        exten_str = ", ".join(exten_list)
        await ctx.send(f"Extensions: {exten_str}")

def setup(bot):
    bot.add_cog(CogControl(bot))