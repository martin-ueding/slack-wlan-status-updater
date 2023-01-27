import abc
import datetime
import json
import urllib.request
from typing import Sequence


class StatusSetter(abc.ABC):
    @abc.abstractmethod
    def set_status(self, emoji: str, text: str, expiration: datetime.datetime) -> None:
        raise NotImplementedError()


class SlackStatusSetter(StatusSetter):
    def __init__(self, name: str, token: str):
        self._name = name
        self._token = token

    def set_status(self, emoji: str, text: str, expiration: datetime.datetime) -> None:
        print(f"Setting status for “{self._name}” to “:{emoji}: {text}” …")
        data = {
            "profile": {
                "status_emoji": f":{emoji}:",
                "status_text": text,
                "status_expiration": expiration.timestamp(),
            }
        }
        url = "https://slack.com/api/users.profile.set"
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self._token}",
        }
        request = urllib.request.Request(
            url, data=json.dumps(data).encode(), headers=headers
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            assert response.status == 200
            response_data = json.loads(response.read().decode())
            assert response_data["ok"], response_data


class InterceptingSlackStatusSetterDecorator(StatusSetter):
    def __init__(self, status_setter: StatusSetter):
        self._status_setter = status_setter
        self._last_status = None

    def set_status(self, emoji: str, text: str, expiration: datetime.datetime) -> None:
        new_status = (emoji, text, expiration)
        if new_status != self._last_status:
            self._status_setter.set_status(emoji, text, expiration)
            self._last_status = new_status


class MultiStatusSetter(StatusSetter):
    def __init__(self, status_setters: Sequence[StatusSetter]):
        self._status_setters = status_setters

    def set_status(self, emoji: str, text: str, expiration: datetime.datetime) -> None:
        for status_setter in self._status_setters:
            status_setter.set_status(emoji, text, expiration)
