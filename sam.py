import discord
import config
import asyncio
import random
from tprint import log
from sorter import Sorter
from inviter import Inviter
from referral_patrol import ReferralPatrol
from channel_creator import VoiceChannelCreator


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)

        self.main_guild = None
        self.main_channel = None
        self.command_channel = None
        self.create_voice_channel = None

        self.color_change_message = None
        self.invite_create_message = None
        self.shuffle_roles_message = None
        self.command_messages = {}

        self.color_roles = {}

        self.sorter = Sorter()
        self.inviter = Inviter()
        self.referral_patrol = ReferralPatrol()
        self.channel_creator = VoiceChannelCreator()

    # Некрасивый фикс, но без этого не работает
    @staticmethod
    def fix_emoji(emoji):
        if emoji == '⚔':
            return '⚔️'
        if emoji == '⚔️':
            return '⚔'
        if emoji == '🗡':
            return '🗡️'
        if emoji == '🗡️':
            return '🗡'
        if emoji == '㊙':
            return '㊙️'
        if emoji == '㊙️':
            return '㊙'
        return emoji

    async def load_entities(self):
        self.main_guild = self.get_guild(config.main_guild_id)
        self.main_channel = self.get_channel(config.main_channel_id)
        self.command_channel = self.get_channel(config.command_channel_id)
        self.create_voice_channel = self.get_channel(config.create_voice_channel_id)

        self.color_change_message = await self.command_channel.fetch_message(config.color_change_message_id)
        self.invite_create_message = await self.command_channel.fetch_message(config.invite_create_message_id)
        self.shuffle_roles_message = await self.command_channel.fetch_message(config.shuffle_roles_message_id)

        self.command_messages = {
            self.color_change_message.id: self.color_change_message,
            self.invite_create_message.id: self.invite_create_message,
            self.shuffle_roles_message.id: self.shuffle_roles_message,
        }

        for message in self.command_messages.values():
            await message.clear_reactions()

    async def reload_color_roles(self):
        self.color_roles.clear()
        for role in self.main_guild.roles:
            if role.id in config.basic_role_id_order:
                self.color_roles[role.name.split()[0]] = role

    async def prepare_shuffle_roles_message(self):
        await self.shuffle_roles_message.add_reaction(config.shuffle_emoji)
        await asyncio.sleep(0.2)
        await self.shuffle_roles_message.add_reaction(config.back_emoji)

    async def prepare_messages(self):
        for emoji in self.color_roles.keys():
            await self.color_change_message.add_reaction(self.fix_emoji(emoji))

        await self.invite_create_message.add_reaction(config.invite_emoji)

        await self.prepare_shuffle_roles_message()

    async def swap_color_role(self, member, to):
        roles = list(member.roles)
        for role in member.roles:
            if role in self.color_roles.values():
                roles.remove(role)
        roles.append(to)
        if set(member.roles) != set(roles):
            await member.edit(roles=roles)

    async def on_raw_reaction_add(self, payload):
        if self.user.id == payload.user_id:
            return

        if payload.message_id in self.command_messages:
            member = self.main_guild.get_member(payload.user_id)

            if payload.message_id == self.color_change_message.id:
                await self.swap_color_role(member, self.color_roles[self.fix_emoji(str(payload.emoji))])

            if payload.message_id == self.shuffle_roles_message.id and not self.sorter.busy:
                await self.shuffle_roles_message.clear_reactions()
                await self.shuffle_roles_message.add_reaction(config.wait_emoji)
                if str(payload.emoji) == config.shuffle_emoji:
                    await self.sorter.sort(self, original=False)
                elif str(payload.emoji) == config.back_emoji:
                    await self.sorter.sort(self, original=True)
                await self.shuffle_roles_message.clear_reactions()
                await self.prepare_shuffle_roles_message()

            if payload.message_id == self.invite_create_message.id:
                invite_text = await self.inviter.generate_invite(member, self.main_channel, self)
                if invite_text:
                    try:
                        await member.send(invite_text)
                    except Exception as e:
                        log(e)
                        invite_text = config.error_template.replace('<mention>', member.mention) + invite_text
                        try:
                            await self.main_channel.send(invite_text)
                        except Exception as e:
                            log(e)

            await self.command_messages[payload.message_id].remove_reaction(payload.emoji, member)

    async def set_game(self):
        activity = discord.Activity(name=config.game_name, type=discord.ActivityType.watching)
        await self.change_presence(activity=activity, status=discord.Status.online)

    async def on_ready(self):
        log('Вошёл под', self.user)
        await self.set_game()
        await self.load_entities()
        await self.reload_color_roles()
        await self.prepare_messages()

        await self.referral_patrol.refresh(self.main_guild)
        log('Загрузка завершена!')

    async def give_random_color_role(self, member):
        role = random.choice(list(self.color_roles.values()))
        await member.add_roles(role)
        return role

    async def on_member_join(self, member):
        await self.wait_until_ready()

        issued_role = await self.give_random_color_role(member)
        inviters = await self.referral_patrol.detect(self.main_guild)

        message = config.welcome_message\
            .replace('<mention>', member.mention)\
            .replace('<role>', issued_role.mention)

        invite_message = config.invite_detection_message

        if len(inviters) == 0:
            invite_message = ''
        elif len(inviters) == 1:
            invite_message = invite_message\
                .replace('<inviter>', inviters[0].mention)\
                .replace('<lol_message>', '')
        elif len(inviters) >= 2:
            invite_message = invite_message\
                .replace('<inviter>', ' или '.join([i.mention for i in inviters]))\
                .replace('<lol_message>', config.lol_message)

        message = message.replace('<invite_detection_message>', invite_message)

        await self.main_channel.send(message)

    async def on_voice_state_update(self, member, before, after):
        await self.wait_until_ready()

        await self.channel_creator.handle(member, before, after, client)


intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.guild_reactions = True

client = MyClient(intents=intents)
client.run(config.token)
