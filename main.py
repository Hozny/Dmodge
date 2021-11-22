import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from dmodge import Dmodge
from dmoj_client import DmojClient
from contest_manager import ContestManager

def setup(client):
    dmoj_client = DmojClient()

    client.add_cog(Dmodge(client, dmoj_client))
    client.add_cog(ContestManager(client, dmoj_client))

if __name__ == "__main__":
    load_dotenv()
    DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    setup(client)
    client.run(DISCORD_CLIENT_SECRET)

