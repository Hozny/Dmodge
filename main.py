import discord
from discord.ext import commands

from dmodge import Dmodge

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def setup(client):
    client.add_cog(Dmodge(client))

setup(client)
client.run('OTA1NjMyMzY5MTk5OTU2MDE4.YYM53g.6oR1zxNhIZnyF9Y8I-hFfRfK5k4')
