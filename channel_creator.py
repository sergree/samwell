import asyncio
import random
import config
from tprint import log


class VoiceChannelCreator:
    def __init__(self):
        self.created_channels = []

    def get_max_position(self):
        return max([ch.position for ch in self.created_channels])

    # Опять сложности Emoji
    @staticmethod
    def fix_emoji(emoji):
        if emoji in ['⚔', '⚔️']:
            return '🐴'
        return emoji

    async def handle(self, member, before, after, client):

        if after.channel == client.create_voice_channel:
            await client.create_voice_channel.set_permissions(member, connect=False)
            new_channel = await client.main_guild.create_voice_channel(
                name=f'{self.fix_emoji(random.choice(list(client.color_roles.keys())))} {random.choice(config.lore_channel_names)}',
                position=self.get_max_position() if self.created_channels else client.create_voice_channel.position,
                category=client.create_voice_channel.category
            )
            self.created_channels.append(new_channel)
            await member.edit(voice_channel=new_channel)
            await asyncio.sleep(60)
            await client.create_voice_channel.set_permissions(member, overwrite=None)

        for channel in list(self.created_channels):
            if len(channel.members) == 0:
                try:
                    await channel.delete()
                except Exception as e:
                    log(e)
                self.created_channels.remove(channel)
