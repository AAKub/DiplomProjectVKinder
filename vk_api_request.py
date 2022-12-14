import requests
import datetime


class VkUser:
    BASE_URL = "https://api.vk.com/method/"
    PROTOCOL_VERSION = "5.131"
    METHOD_USERS_GET = "users.get"
    FIELDS = {
        'bdate': 'день рождения',
        'sex': 'пол',
        'city': 'город',
        'relation': 'семейное положение'
    }
    METHOD_USERS_SEARCH = "users.search"
    COUNT_USERS_SEARCH = 10
    METHOD_PHOTOS_GET = "photos.get"
    COUNT_PHOTOS_GET = 1000

    def __init__(self, token=None, user_id=1):
        self.token = token
        self.user_id = user_id

    def get_token(self):
        AUTH_LINK = 'https://oauth.vk.com/authorize?client_id=' + self.user_id + '&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=status.offline&response_type=token&v=' + self.PROTOCOL_VERSION
        return 'Токен можно получить по этой ссылке: ' + AUTH_LINK

    def get_url(self, method_name):
        return f'{self.BASE_URL}{method_name}'

    def users_get(self):
        url = self.get_url(self.METHOD_USERS_GET)
        params = {
            'access_token': self.token,
            'user_ids': self.user_id,
            'fields': ', '.join(f'{k}' for k in self.FIELDS.keys()),
            'v': self.PROTOCOL_VERSION
        }
        response = requests.get(url, params=params)
        self.check_user_info(response.json())
        return response.json()

    def check_user_info(self, user_info):
        empty_fields = ''
        for k, v in self.FIELDS.items():
            if k not in user_info['response'][0].keys():
                empty_fields += v + ', '
        if empty_fields != '':
            print('Заполните недостающие данные: ', empty_fields)
            exit()

    def prepare_params_for_users_search(self, user_info):
        params_for_users_search = {}
        params_for_users_search['city'] = user_info['response'][0]['city']['id']
        if user_info['response'][0]['sex'] == 1:
            params_for_users_search['sex'] = 2
        else:
            params_for_users_search['sex'] = 1

        return params_for_users_search

    def users_search(self, params_for_users_search, AGE_FROM, AGE_TO):
        url = self.get_url(self.METHOD_USERS_SEARCH)
        params = {
            'access_token': self.token,
            'count': self.COUNT_USERS_SEARCH,
            'city': params_for_users_search['city'],
            'sex': params_for_users_search['sex'],
            'age_from': AGE_FROM,
            'age_to': AGE_TO,
            'v': self.PROTOCOL_VERSION,
            'has_photo': 1,
            'offset': 20
        }
        response = requests.get(url, params=params)
        return response.json()['response']['items']

    def get_ids_searched_people(self, searched_people):
        ids_list = []
        for people in searched_people:
            ids_list.append(people['id'])
        return ids_list

    def photos_get(self, owner_id):
        url = self.get_url(self.METHOD_PHOTOS_GET)
        params = {
            'access_token': self.token,
            'count': self.COUNT_PHOTOS_GET,
            'album_id': 'profile',
            'extended': 1,
            'owner_id': owner_id,
            'v': self.PROTOCOL_VERSION
        }
        response = requests.get(url, params=params)
        return response.json()['response']['items']


