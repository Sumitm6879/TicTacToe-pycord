import discord
from discord.ext import commands
import tic
bot = commands.Bot(command_prefix=">")

tic.setup(bot)

@bot.event
async def on_ready():
	print("Bot is Ready!")

bot.run("YOUR_BOT_TOKEN")
