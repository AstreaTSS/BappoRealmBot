import discord
from datetime import datetime

class Countdown():
    def __init__(self, name, color, channel_id, time):
        self.name = name
        self.color = discord.Color(int(color, 0))
        self.channel_id = channel_id
        self.time = int(time)