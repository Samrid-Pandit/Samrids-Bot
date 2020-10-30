from discord.ext import commands, tasks
import discord
import os
from itertools import cycle
import json	
import pymongo
import motor
from dotenv import load_dotenv
# from flask_site import keep_alive


"""
Loads all the files from .env
"""
load_dotenv()


"""
Prints "-------------------------"
"""
def star():
	print("-----------------------------------------------")


"""
Checks if it is in a local machine
"""
try:
	print(os.environ['TEST'])
	is_local = True
	star()
	print("The Bot Is Being Hosted Locally (On Samrid's PC)")
	star()
except Exception:
	star()
	print("The Bot Is Not Being Hosted Locally (NOT ON SAMRID's PC)")
	star()
	is_local = False


"""
Statuses
"""
status = cycle(['Your THICC Ass', 'Gay Porn', '-_-', 'When you will die!'])


"""
Mongo Db
"""
mongoclient = os.environ['MONGOCLIENT']
bot = pymongo.MongoClient(mongoclient)
db = bot.ihihihibot_db
if is_local:
	prefixes = db.server_test_prefixes
else:
	prefixes = db.server_prefixes


"""
Function to get prefix for each server
"""
def get_prefix(client,message):
	cur = prefixes.find_one({'server_id':message.guild.id})
	return(cur.get('prefix'))

"""
Discord.py Variables
"""
token = os.environ['TOKEN']
defualt_prefix = "."
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = get_prefix, case_insensitive=True, intents=intents)


"""
This Background task loops every 1 hour and changes the status!
"""
@tasks.loop(seconds = 3600)
async def change_status():
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"""{next(status)} || {defualt_prefix}help"""))


"""
It initializes all the background tasks as soon as it is ready!
"""
@client.event
async def on_ready():
	
	try:
		change_status.start()
	except Exception:
		pass
	star()
	print("GOD HAS AWOKEN!")
	star()
	
	for guild in client.guilds:
		
		if prefixes.count_documents({'server_id' : guild.id}) == 0:
			perfix_data = {
				'server_id' : guild.id,
				'prefix' : defualt_prefix,
				'server_name' : guild.name
			}
			prefixes.insert_one(perfix_data)
			print(f"Prefix for server id {guild.id} has been created!")			
			star()
"""
Loads the cogs
"""
@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')
	await ctx.send(f'The Plugin {extension} has been enabled!')


"""
unloads the cogs
"""
@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	await ctx.send(f'The Plugin {extension} has been disabled!')


"""
Reloads the cogs
"""
@client.command()
async def reload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')
	client.load_extension(f'cogs.{extension}')
	await ctx.send(f"The Plugin {extension} has been reloaded!")


"""
It updates the database whenever it joins a new guild!
"""
@client.event
async def on_guild_join(guild):
	if prefixes.count_documents({'server_id' : guild.id}) == 0:
			perfix_data = {
				'server_id' : guild.id,
				'prefix' : defualt_prefix,
				'server_name' : guild.name
			}
			prefixes.insert_one(perfix_data)
			print(f"Prefix for server id {guild.id} has been created!")
			star()


"""
On message event (Whenever a message is written!)
"""
@client.event
async def on_message(msg):
	try:
		if msg.mentions[0] == client.user and not msg.author.bot:
			cur = prefixes.find_one({'server_id':msg.guild.id})
			pre = cur.get('prefix')
			await msg.channel.send(f"My prefix for this server is `{pre}`")
	except:
		pass
	await client.process_commands(msg)


"""
Changes the prefix for that server by updating the database!
"""
@client.command()
@commands.has_permissions(administrator = True)
async def changeprefix(ctx,*, prefix):

	cur = prefixes.find_one({'server_id':ctx.guild.id})
	old_prefix = cur.get('prefix')

	old_data = {
				'server_id':ctx.guild.id, 
				'prefix':old_prefix
	}
	new_data = {"$set": {
						'server_id':ctx.guild.id, 
						'prefix': prefix
				}
	}

	prefixes.update_one(old_data, new_data)
	print(f"Prefix for the server {ctx.guild.id} has been updated to '{prefix}' !")
	star()
	await ctx.send(f"The prefix was changed to {prefix}")


"""
Gives you the prefix for the guild you are in!
"""
@client.command()
async def prefix(ctx):
	cur = prefixes.find_one({'server_id':ctx.guild.id})
	prefix = cur.get('prefix')
	await ctx.send(f"My prefix for this server is {prefix}")

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f"cogs.{filename[:-3]}")

# keep_alive()
client.run(token)
	
