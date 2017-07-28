import enum
import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger('pyslackers.website.util')


class SlackException(Exception):
    """Exception to wrap any issues specific to Slack's
    ok: false field in their responses vs an HTTP related
    issue."""


class _SlackMethod(enum.Enum):
    ADMIN_INVITE = 'users.admin.invite'
    USER_LIST = 'users.list'

    @property
    def url(self):
        return f'https://slack.com/api/{self.value}'


class SlackClient:
    __slots__ = ('_token', '_session')

    def __init__(self, token: str):
        self._token = token
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
        })

    def invite(self, email: str, channels: List[str], *, resend: bool = True):
        logger.info('Sending slack invite to %s', email)
        r = self._session.post(_SlackMethod.ADMIN_INVITE.url,
                               data={
                                   'token': self._token,
                                   'email': email,
                                   'channels': ','.join(channels),
                                   'resend': resend,
                               })
        r.raise_for_status()
        body = r.json()
        if not body['ok']:
            logger.error('Error sending invite: %s', body)
        return body['ok']

    def members(self) -> List[Dict[str, Any]]:
        logger.info('Retrieving user list from slack')
        r = self._session.get(_SlackMethod.USER_LIST.url,
                              params={
                                  'token': self._token,
                                  'presence': True
                              })
        r.raise_for_status()
        body = r.json()
        if not body['ok']:
            logger.error('Unable to retrieve slack user list: %s', body)
            raise SlackException(body['error'])
        return r.json()['members']
