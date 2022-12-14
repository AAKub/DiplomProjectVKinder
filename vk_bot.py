from random import randrange


class VkBot:
    def __init__(self, user_id, vk):
        self.user_id = user_id,
        self.vk = vk

    def write_msg(self, message):
        self.vk.method('messages.send', {
            'user_id': self.user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        })