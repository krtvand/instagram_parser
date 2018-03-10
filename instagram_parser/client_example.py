import json
import datetime

from instagram_parser.main import parse_instagram

date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=40)
date_till = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
location_id = '224829075'

result = parse_instagram(location_id=location_id, date_from=date_from, date_till=date_till)
print(json.dumps(result))

with open('parsing_results', 'w') as f:
    f.write(json.dumps(result))
