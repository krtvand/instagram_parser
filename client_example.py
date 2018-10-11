import json
import datetime

from instagram_parser.parse_publications_by_location import parse_publications_by_location
from instagram_parser.parse_publications_by_tag import parse_publications_by_tag
from instagram_parser.parse_user_following import parse_user_following


date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=40)
date_till = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
location_id = '224829075'
tag = 'yandex'
username = 'mordovian_air'

locations_result = parse_publications_by_location(location_id=location_id, date_from=date_from, date_till=date_till)
print(json.dumps(locations_result))

tag_result = parse_publications_by_tag(tag=tag, date_from=date_from, date_till=date_till)
print(json.dumps(locations_result))

# :param login: логин аккаунта, от имени которого будет выполнена авторизация в instagram
# :param password: пароль аккаунта, от имени которого будет выполнена авторизация в instagram
# :param username: пользователь instagram, для которого необходимо собрать данные о подписках
login = 'enter_login_there'
password = 'enter_pass_there'
user_following = parse_user_following(login=login, password=password, username=username)
print(json.dumps(user_following))


