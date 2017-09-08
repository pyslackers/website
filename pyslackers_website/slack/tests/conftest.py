import uuid

import pytest

from pyslackers_website.slack.util import SlackClient


@pytest.fixture()
def fake_token():
    yield str(uuid.uuid4())


@pytest.fixture()
def slack_client(fake_token: str):
    yield SlackClient(fake_token)
