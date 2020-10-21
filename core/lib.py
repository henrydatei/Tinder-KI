import time
from datetime import datetime
from pprint import pprint
from random import randint
from urllib.parse import urljoin
import json

import requests

from core.cls import Recommendation, Match, Person, Profile, Message


class TinderAPI:
    headers = {}
    x_auth_token = None
    base_url = "https://api.gotinder.com"

    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'

    def __init__(self, x_auth_token):
        self.x_auth_token = x_auth_token
        self.init_headers()
        #self.match_person_ids = [m.person.person_id for m in self.matches]
        self.profile = self.get_profile()

    def init_headers(self):
        self.headers['User-agent'] = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
        self.headers['Content-type'] = "application/json"
        if not self.x_auth_token:
            raise AttributeError('x_auth_token is not set')

        self.headers['X-Auth-Token'] = self.x_auth_token

    def request(self, url, method=GET, data=None, params=None, *args, **kwargs):
        _url = urljoin(self.base_url, url)
        if method is self.GET:
            r = requests.get(url=_url, params=params or None, headers=self.headers, **kwargs)
        elif method is self.POST:
            r = requests.post(url=_url, data=data or None, headers=self.headers, *args, **kwargs)
        elif method is self.DELETE:
            r = requests.delete(url=_url, headers=self.headers, **kwargs)
        else:
            raise AttributeError('Please check method parameter')

        if r.status_code != 200:
            pprint(r.__dict__)
            raise Exception("Error while requesting '%s'\n (%s)" % (_url, r.content))

        return r

    def get_user_recs(self):
        """

        :return: Returns recommendations
        :rtype: list of Recommendation
        """
        r = self.request('/user/recs')
        recs = []
        for rec in r.json().get('results', []):
            recs.append(Recommendation(**{
                'bio': rec.get('bio'),
                'name': rec.get('name'),
                'user_id': rec.get('_id'),
            }))
        return recs

    def get_profile(self):
        r = self.request('/profile')
        if not r.status_code == 200:
            return
        return Profile(
            user_id=r.json().get('_id')
        )

    def like(self, user_id):
        r = self.request('/like/{user_id}'.format(user_id=user_id))
        data = r.json()
        if data.get('likes_remaining', 0) < 1:
            date = datetime.fromtimestamp(data.get('rate_limited_until') / 1000)
            print("No more likes -- have to wait until %s" % date)
            _delta = date - datetime.now()
            print("Waiting %i seconds" % _delta.seconds)
            time.sleep(_delta.seconds)
            return False
        return {
            'likes_remaining': data.get('likes_remaining'),
            'match': data.get('match'),
        } if r.status_code == 200 else False

    def dislike(self, user_id):
        r = self.request('/pass/{user_id}'.format(user_id=user_id))
        return r if r.status_code == 200 else False

    def unmatch(self, match_id):
        return self.request("/user/matches/{match_id}".format(match_id=match_id), method=self.DELETE)

    def matches_page(self, data):
        matches = []
        for match in data.get('matches'):
            msgs = []
            for msg in match.get('messages', []):
                m = Message(**{
                    "message_id": msg.get('_id'),
                    "match_id": msg.get('match_id'),
                    "sent_date": msg.get('sent_date'),
                    "message": msg.get('message'),
                    "message_to": msg.get('to'),
                    "message_from": msg.get('from'),
                    "timestamp": msg.get('timestamp')
                })
                msgs.append(m)
            p = Person()
            p.person_id = match['person'].get('_id')
            p.birth_date = match['person'].get('birth_date')
            photoObj =  match['person'].get('photos')
            p.photo_urls = [photo.get('url') for photo in photoObj]
            p.name = match['person'].get('name')

            m = Match(**{
                'message_count': match['message_count'],
                'match_id': match['id'],
                'person': p,
                'last_message': msgs,
                'created_date': match['created_date'],
            })
            matches.append(m)
        return matches

    def matches(self):
        params = {
            'messages': 0,
            'count': 100,
            'is_tinder_u': 'false',
            'locale': 'de'
        }
        r = self.request('/v2/matches', params=params)
        data = r.json().get('data', None)

        m = self.matches_page(data)
        next_page_token = data.get('next_page_token')

        while next_page_token is not None:
            params = {
                'messages': 0,
                'count': 100,
                'is_tinder_u': 'false',
                'locale': 'de',
                'page_token': next_page_token
            }
            r = self.request('/v2/matches', params=params)
            data = r.json().get('data', None)
            more = self.matches_page(data)
            m.extend(more)
            next_page_token = data.get('next_page_token')

        return m

    def message(self, to_id, message):
        match_id = to_id + self.profile.user_id
        return self.request('/user/matches/{user_id}'.format(user_id=match_id), method=TinderAPI.POST, json={"message": message})

    def getChat(self, match_id, next_page_token = None):
        if next_page_token is None:
            params = {
                'count': 100,
                'locale': 'de',
            }
        else:
            params = {
                'count': 100,
                'locale': 'de',
                'page_token': next_page_token
            }
        r = self.request('/v2/matches/{match_id}/messages'.format(match_id=match_id), params=params)
        data = r.json().get('data', None)
        messages = []

        for msg in data.get('messages'):
            m = Message(**{
                "message_id": msg.get('_id'),
                "match_id": msg.get('match_id'),
                "sent_date": msg.get('sent_date'),
                "message": msg.get('message'),
                "message_to": msg.get('to'),
                "message_from": msg.get('from'),
                "timestamp": msg.get('timestamp')
            })
            messages.append(m)

        next_page_token = data.get('next_page_token')
        if next_page_token is not None:
            moreMessages = self.getChat(match_id, next_page_token)
            messages.extend(moreMessages)
        return messages
