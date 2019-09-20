import datetime


class ReferralPatrol:
    def __init__(self):
        self.invites = []
        self.last_refreshed_at = None
        self.invite_to_member = {}

    async def refresh(self, guild, preloaded_invites=None):
        self.invites.clear()
        if not preloaded_invites:
            new_invites = await guild.invites()
        else:
            new_invites = preloaded_invites
        for invite in new_invites:
            if invite.inviter == guild.me and invite.max_age != 0:
                self.invites.append(invite)
        for invite in list(self.invite_to_member.keys()):
            if invite not in self.invites:
                del self.invite_to_member[invite]
        self.last_refreshed_at = datetime.datetime.now()

    async def new(self, invite, member):
        self.invite_to_member[invite] = member
        await self.refresh(member.guild)

    async def detect(self, guild):
        new_invites = await guild.invites()

        for invite in list(self.invites):
            if invite in new_invites:
                self.invites.remove(invite)
            else:
                expire_at = invite.created_at + datetime.timedelta(hours=3) + datetime.timedelta(seconds=invite.max_age)
                if datetime.datetime.now() > expire_at:
                    self.invites.remove(invite)

        detected_inviters = []

        for invite in self.invites:
            detected = self.invite_to_member.get(invite)
            if detected:
                detected_inviters.append(detected)

        await self.refresh(guild, preloaded_invites=new_invites)

        return detected_inviters
