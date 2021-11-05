import discord
from discord.ext import commands
import os

from dmodge import Dmodge

DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def setup(client):
    client.add_cog(Dmodge(client))

setup(client)
client.run(DISCORD_CLIENT_SECRET)
