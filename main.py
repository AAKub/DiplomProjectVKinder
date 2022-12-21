from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from model import Base, User, Candidate, Photo
from vk_api_request import VkUser
from vk_api_request import get_token
from my_token import TOKEN, GROUP_TOKEN
from vk_bot import VkBot
from pprint import pprint
import time


CLIENT_ID = '51502867'
DB_URL = 'postgresql://postgres:***@localhost/vkinder_db'

vk = VkApi(token=GROUP_TOKEN)
long_poll = VkLongPoll(vk)

engine = create_engine(DB_URL, echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()
GREETING = """Привет, {}.
Я - чат-бот социальной сети "ВКонтакте".
Я помогу тебе подобрать пару.
"""

for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        USER_ID = event.user_id
        bot = VkBot(USER_ID, vk, session)
        bot.write_msg(GREETING.format(USER_ID))
        break
bot.write_msg(get_token(CLIENT_ID))
for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        USER_TOKEN = event.text
        vk_client = VkUser(TOKEN, USER_ID)
        user_info = vk_client.users_get()
        if isinstance(user_info, str):
            bot.write_msg(user_info)
            exit()
        if user_info is None:
            bot.write_msg('Сервер не отвечает. Попробуйте позже...')
            exit()
        break


bot.write_msg('Введите минимальный возраст для поиска -> ')
for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        try:
            if 16 <= int(event.text) <= 100:
                AGE_FROM = int(event.text)
                break
            else:
                bot.write_msg('Введите корректный возраст от 16 до 100')
        except ValueError:
            bot.write_msg('Введите числовое значение')

bot.write_msg('Введите максимальный возраст для поиска -> ')
for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        try:
            if 16 <= int(event.text) <= 100 and int(event.text) >= AGE_FROM:
                AGE_TO = int(event.text)
                break
            else:
                bot.write_msg('Введите корректный возраст от минимального до 100')
        except ValueError:
            bot.write_msg('Введите числовое значение')

params_for_users_search = vk_client.prepare_params_for_users_search(user_info)
user = session.query(User).filter(User.id == USER_ID).first()
candidates = vk_client.users_search(params_for_users_search, AGE_FROM, AGE_TO, USER_ID, session)
if candidates is None:
    bot.write_msg('Сервер не отвечает. Попробуйте позже...')
    exit()
for candidate in candidates:
    # time.sleep(0.2)
    top_photos = vk_client.photos_get(candidate['id'])
    if top_photos is None:
        bot.write_msg('Сервер не отвечает. Попробуйте позже...')
        exit()
    result = f"{candidate['first_name']} {candidate['last_name']}\n"
    result += f"https://vk.com/{candidate['screen_name']}\n"
    candidate_exists = session.query(Candidate).filter(Candidate.id == candidate['id']).first()
    if not candidate_exists:
        c = Candidate(
            id=candidate['id'],
            first_name=candidate['first_name'],
            last_name=candidate['last_name'],
            screen_name=candidate['screen_name']
        )
        session.add(c)
        user.candidates.append(c)
    else:
        user.candidates.append(candidate_exists)

    bot.write_msg(result)

    attachments = []
    for photo in top_photos:
        owner_photo_id = f"photo{photo['owner_id']}_{photo['id']}"
        attachments.append(owner_photo_id)
        photo_exists = session.query(Photo).filter(Photo.id == owner_photo_id).first()
        if not photo_exists:
            session.add(
                Photo(
                    id=owner_photo_id,
                    candidate_id=photo['owner_id']
                )
            )
    bot.send_attachment(','.join(attachments))

session.commit()