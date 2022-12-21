import requests
import datetime
from model import User

PROTOCOL_VERSION = "5.131"

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
        if response.status_code == 200:
            check = self.check_user_info(response.json())
            if check is not None:
                return check
            return response.json()
        else:
            return

    def check_user_info(self, user_info):
        empty_fields = ', '.join(f'{v}' for k, v in self.FIELDS.items() if k not in user_info['response'][0].keys())
        if empty_fields != '':
            return 'Заполните недостающие данные: ' + empty_fields
        return

    def prepare_params_for_users_search(self, user_info):
        params_for_users_search = {}
        params_for_users_search['city'] = user_info['response'][0]['city']['id']
        if user_info['response'][0]['sex'] == 1:
            params_for_users_search['sex'] = 2
        else:
            params_for_users_search['sex'] = 1

        return params_for_users_search

    def users_search(self, params_for_users_search, AGE_FROM, AGE_TO, user_id, session):
        url = self.get_url(self.METHOD_USERS_SEARCH)
        params = {
            'access_token': self.token,
            'count': self.COUNT_USERS_SEARCH,
            'fields': 'screen_name',
            'city': params_for_users_search['city'],
            'sex': params_for_users_search['sex'],
            'age_from': AGE_FROM,
            'age_to': AGE_TO,
            'v': self.PROTOCOL_VERSION,
            'has_photo': 1,
            'offset': 78
        }
        def already_matched(user_id, candidate_id):
            user = session.query(User).filter(User.id == user_id, User.candidates.any(id=candidate_id)).first()
            return user is not None
        response = requests.get(url, params=params)
        if response.status_code == 200:
            response = response.json()['response']
            items = [item for item in response['items'] if
                     not item['is_closed'] and not already_matched(user_id, item['id'])]
            return items
        else:
            return

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
        if response.status_code == 200:
            response = response.json()
            items = response['response']['items']

            def count_likes_and_comments(item):
                return item['likes']['count'] + item['comments']['count']

            items.sort(key=count_likes_and_comments)
            top_photos = items[-3:]
            return top_photos
        else:
            return

def get_token(client_id):
    AUTH_LINK = 'https://oauth.vk.com/authorize?client_id=' + client_id + '&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=status.offline&response_type=token&v=' + PROTOCOL_VERSION
    return 'Для начала поиска напишите ваш токен. Токен можно получить по этой ссылке: ' + AUTH_LINK
