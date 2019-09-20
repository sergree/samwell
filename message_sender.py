import discord
import config

client = discord.Client()


def create_embed(title, description, thumbnail, footer=None):

    embed = discord.Embed(
        title=title,
        color=0x002568,
        description=description
    )

    embed.set_thumbnail(url=thumbnail)
    embed.set_author(
        name='Сиеста Ванилла',
        icon_url=r'https://media.discordapp.net/attachments/581368009566715910'
                 r'/624304138360061962/vanilla.png?width=676&height=676')

    if footer:
        embed.set_footer(text=footer)

    return embed

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    channel = client.get_channel(config.command_channel_id)

    await channel.send(
        embed=create_embed(
            'Изменение роли',
            """Если Вам не нравится цвет Вашего ника или положение в списке пользователей, Вы можете изменить свою роль.

Нажмите на соответствующую **Эмодзи** ниже.""",
            'https://media.discordapp.net/attachments/581368009566715910/624301629897834507/personality-behavior-character-role-action-512.png'
        )
    )

    await channel.send(
        embed=create_embed(
            'Перемешивание ролей',
            """Если Вас не устраивает текущий порядок ролей в списке, Вы можете изменить его.

Нажмите `🔄`, чтобы перемешать роли в случайном порядке.
Нажмите `🔙`, чтобы вернуть изначальный порядок.""",
            'https://media.discordapp.net/attachments/581368009566715910/624301624978046978/UI_Blue_2_of_3_30-512.png'
        )
    )

    await channel.send(
        embed=create_embed(
            'Приглашение друга',
            """Если Вы хотите пригласить Вашего друга на наш сервер, Вы можете создать приглашение.

Нажмите `➕`, чтобы создать одноразовое приглашение.""",
            'https://media.discordapp.net/attachments/581368009566715910/624301628228632576/invitation-512.png',
            footer='Данной функцией можно воспользоваться не более одного раза в день.'
        )
    )

    await client.logout()


client.run(config.token)