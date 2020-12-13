from datetime import datetime, timedelta, timezone

import pytz
from dateutil.parser import parse



class Recommendation:
    user_id = None
    bio = None
    name = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))


class Person:
    person_id = None
    birth_date = None
    name = None
    photo_urls = None
    bio = None
    gender = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))


class Message:
    message_id = None
    message_from = None
    match_id = None
    message = None
    sent_date = None
    timestamp = None
    message_to = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))

    def sent_date_time_ago(self):
        """
        :rtype: timedelta
        """
        sent = parse(self.sent_date)
        return datetime.now(pytz.utc) - sent


class Match:
    message_count = None
    match_id = None
    person = None
    last_message = []
    created_date = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))

    def created_time_ago(self):
        """
        :return:
        :rtype datetime.timedelta
        """
        created = parse(self.created_date)
        return datetime.now(pytz.utc) - created


class Profile:
    user_id = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs.get(key))
