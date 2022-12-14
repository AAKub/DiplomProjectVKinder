from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api_request import VkUser
from my_token import TOKEN
from vk_bot import VkBot
from pprint import pprint
import time

GREETING = """Привет, меня зовут VKinder.
Я - чат-бот социальной сети "ВКонтакте".
Я помогу тебе подобрать пару.
 А как тебя зовут? (твой ID ВКонтакте)"""
# USER_ID = input(GREETING)
USER_ID = '221116652'
AGE_FROM = int(input('Введите минимальный возраст для поиска -> '))
AGE_TO = int(input('Введите максимальный возраст для поиска -> '))

GROUP_TOKEN = 'vk1.a.WuMWkWX715EJBTdtqiaO6P5H1R42gA6q2_kDyC7on96imGkWiBZymzK3tUB7E4PuLaJK1NDDs37aKrHCUytVTLlKSDtBMb2IAOpYseEuE06dIKR9m0ccPRYnAvy0stfajx6LB8abCo2hv_CQxpwt7BkyayzyX9SssBgLt7WMweGX_LkZVLU8COeU_MGwM3ZO3bif9iY1f9gw3ne2fJm36A'
DSN = 'postgresql://<DB-CONNECTION>'

vk = VkApi(token=GROUP_TOKEN)
long_poll = VkLongPoll(vk)

bot = VkBot(USER_ID, vk)
for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        # request = event.text
        bot.write_msg(f"Хай, {event.user_id}")


vk_client = VkUser(TOKEN, USER_ID)
# print(vk_client.get_token())
user_info = vk_client.users_get()
# print(user_info['response'][0])
params_for_users_search = vk_client.prepare_params_for_users_search(user_info)
searched_people = vk_client.users_search(params_for_users_search, AGE_FROM, AGE_TO)
pprint(searched_people)
ids_searched_people = vk_client.get_ids_searched_people(searched_people)
pprint(ids_searched_people)

for owner_id in ids_searched_people:
    time.sleep(0.5)
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
