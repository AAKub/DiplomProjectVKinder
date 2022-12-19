from random import randrange
from model import User

class VkBot:
    def __init__(self, user_id, vk, session):
        self.user_id = user_id,
        self.vk = vk
        self.session = session
        self.create_user_if_not_exists()

    def create_user_if_not_exists(self):
        exists = self.session.query(User).filter(User.id == self.user_id).first()
        if not exists:
            self.session.add(User(id=self.user_id))
            self.session.commit()

    def write_msg(self, message):
        self.vk.method('messages.send', {
            'user_id': self.user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        })

    def send_attachment(self, attachment):
        self.vk.method('messages.send', {
            'user_id': self.user_id,
            'attachment': attachment,
            'random_id': randrange(10 ** 7)
        })
