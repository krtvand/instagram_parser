import json
import datetime

from instagram_parser.parse_publications_by_location import parse_publications_by_location
from instagram_parser.parse_publications_by_tag import parse_publications_by_tag


date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=40)
date_till = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
location_id = '224829075'
tag = 'yandex'

locations_result = parse_publications_by_location(location_id=location_id, date_from=date_from, date_till=date_till)
print(json.dumps(locations_result))

tag_result = parse_publications_by_tag(tag=tag, date_from=date_from, date_till=date_till)
print(json.dumps(locations_result))

# with open('parsing_results', 'w') as f:
#     f.write(json.dumps(result))

