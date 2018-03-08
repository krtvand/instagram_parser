import json
import datetime

from instagram_parser.main import parse_instagram

DATE_FROM = datetime.datetime.utcnow() - datetime.timedelta(minutes=40)
DATE_TILL = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
location_id = '224829075'

result = parse_instagram()
print(json.dumps(result))

with open('parsing_results', 'w') as f:
    f.write(json.dumps(result))
