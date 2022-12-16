from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api_request import VkUser
from vk_api_request import get_token
from my_token import TOKEN
from vk_bot import VkBot
from pprint import pprint
import time


CLIENT_ID = '51502867'
GROUP_TOKEN = 'vk1.a.WuMWkWX715EJBTdtqiaO6P5H1R42gA6q2_kDyC7on96imGkWiBZymzK3tUB7E4PuLaJK1NDDs37aKrHCUytVTLlKSDtBMb2IAOpYseEuE06dIKR9m0ccPRYnAvy0stfajx6LB8abCo2hv_CQxpwt7BkyayzyX9SssBgLt7WMweGX_LkZVLU8COeU_MGwM3ZO3bif9iY1f9gw3ne2fJm36A'
DB_URL = 'postgresql://postgres:18722009@localhost/vkinder_db'

# AGE_FROM = int(input('Введите минимальный возраст для поиска -> '))
# AGE_TO = int(input('Введите максимальный возраст для поиска -> '))

vk = VkApi(token=GROUP_TOKEN)
long_poll = VkLongPoll(vk)

GREETING = """Привет, {}.
Я - чат-бот социальной сети "ВКонтакте".
Я помогу тебе подобрать пару.
Для начала мне нужно получить от тебя токен..."""

for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        USER_ID = event.user_id
        # request = event.text
        bot = VkBot(USER_ID, vk)
        bot.write_msg(GREETING.format(USER_ID))
        bot.write_msg(get_token(CLIENT_ID))
        vk_client = VkUser(TOKEN, USER_ID)
        user_info = vk_client.users_get()
        if isinstance(user_info, str):
            bot.write_msg(user_info)
            exit()
        break
print(user_info['response'][0])
bot.write_msg('Введите минимальный возраст для поиска -> ')
for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        AGE_FROM = int(event.text)
        break
bot.write_msg('Введите максимальный возраст для поиска -> ')
for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        AGE_TO = int(event.text)
        break

params_for_users_search = vk_client.prepare_params_for_users_search(user_info)
searched_people = vk_client.users_search(params_for_users_search, AGE_FROM, AGE_TO)
pprint(searched_people)
ids_searched_people = vk_client.get_ids_searched_people(searched_people)
pprint(ids_searched_people)

for owner_id in ids_searched_people:
    time.sleep(0.2)
    searched_photo = vk_client.photos_get(owner_id)
    photos = {}
    for photo in searched_photo:
        likes = photo['likes']['count']
        comments = photo['comments']['count']
        for size in photo['sizes']:
            if size['type'] != '':
                url = size['url']

        photos[url] = likes + comments
    top3_photos = sorted(photos.items(), key=lambda x: x[1], reverse=True)[0:3]
    print('Топ 3 фото для id', owner_id, top3_photos)

# pprint(searched_photo)
