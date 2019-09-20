import random
import config


class Sorter:
    def __init__(self):
        self.busy = False

    async def sort(self, client, original=True):
        if self.busy:
            return
        self.busy = True

        if original:
            order = []
            for role_id in config.basic_role_id_order:
                order.append(client.main_guild.get_role(role_id))
        else:
            order = list(client.color_roles.values())
            random.shuffle(order)

        counter = 0
        for role in order:
            counter += 1
            await role.edit(position=counter)

        self.busy = False
