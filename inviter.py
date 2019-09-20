import config
import datetime


class Inviter:

    def __init__(self):
        self.invite_limiter = {}  # {inviter:last_invite_datetime}

    async def generate_invite(self, inviter, channel, client):
        last_invite_created_at = self.invite_limiter.get(inviter, datetime.datetime.min)

        if datetime.datetime.now() - last_invite_created_at < datetime.timedelta(days=1):
            return

        new_invite = await channel.create_invite(max_age=86400, max_uses=1)
        self.invite_limiter[inviter] = datetime.datetime.now()
        await client.referral_patrol.new(new_invite, inviter)

        if new_invite:
            return config.invite_template.replace('<url>', new_invite.url)
