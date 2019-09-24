import discord
import config

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    for guild in client.guilds:
        for role in guild.roles:
            print(guild.name, role.id, role.name)

    await client.logout()


client.run(config.token)