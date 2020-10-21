from core.lib import *
from datetime import datetime, timedelta, timezone
import pytz
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import json

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)

def getAge(person):
    begin = parse(person.birth_date)
    end = datetime.now(pytz.utc)
    num_years = int((end - begin).days / 365.25)
    if begin > yearsago(num_years, end):
        return num_years - 1
    else:
        return num_years

api = TinderAPI("token")

#print(api.profile.user_id)

# for match in api.matches():
#     #print(match.person.name + " - " + str(getAge(match.person)))
#     messages = api.getChat(match.match_id)
#     print(match.match_id + " - " + str(len(messages)))

matches = api.matches()
# for match in matches:
#     try:
#         print(match.person.name + " - " + match.last_message[0].message)
#     except:
#         pass

#print(str(len(matches)))
#print(api.message("5f1e858e8702cc0100e13d9c5f7330dc3b3b1b01000235e4", "Warum hast du mich nicht zuerst angeschrieben?"))

#messages = api.getChat("5f1e858e8702cc0100e13d9c5f7330dc3b3b1b01000235e4")
#print(str(len(messages)))
#for msg in messages:
#    print(msg.message_from + ": " + msg.message)

for match in matches:
    data = {}
    person = match.person
    data['name'] = person.name
    data['id'] = person.person_id
    data['birth_date'] = person.birth_date
    data['age'] = getAge(person)
    data['photo_urls'] = person.photo_urls
    data['match_id'] = match.match_id
    data['messages'] = []
    data['created_date'] = match.created_date
    messages = api.getChat(match.match_id)
    for msg in messages:
        msgObj = {'from': msg.message_from, 'to': msg.message_to, 'time': msg.timestamp, 'content': msg.message}
        data['messages'].append(msgObj)

    with open("chats/" + str(person.person_id) + ".json", 'w') as outfile:
        json.dump(data, outfile)
