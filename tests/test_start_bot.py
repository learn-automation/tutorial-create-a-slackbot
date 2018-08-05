import os

import pytest
from slackclient import SlackClient

from bot import start_bot


def test_initialize_slack_client_type():
    os.environ['BOT_TOKEN'] = 'candy'
    a = start_bot.initialize_slack_client()
    assert isinstance(a, SlackClient)


def test_bot_is_present_in_channel_happy(monkeypatch):
    mock_user = 'godzilla'
    mock_channel = {'channel': {'members': {mock_user}}}
    monkeypatch.setattr(start_bot, 'get_channel_info', lambda *args: mock_channel)
    monkeypatch.setattr(start_bot, 'get_bot_id', lambda *args: mock_user)
    result = start_bot.bot_is_present_in_channel('mock client', mock_channel)
    assert result is True


def test_bot_is_present_in_channel_bot_not_present(monkeypatch):
    mock_user = 'godzilla'
    mock_channel = {'channel': {'members': 'mothra'}}
    monkeypatch.setattr(start_bot, 'get_channel_info', lambda *args: mock_channel)
    monkeypatch.setattr(start_bot, 'get_bot_id', lambda *args: mock_user)
    result = start_bot.bot_is_present_in_channel('mock client', mock_channel)
    assert result is False


def test_is_slack_message_happy():
    mock_event = {'type': 'message'}
    result = start_bot.is_slack_message(mock_event)
    assert result is True


def test_is_slack_message_not_message():
    mock_event = {'type': 'taco'}
    result = start_bot.is_slack_message(mock_event)
    assert result is False


def test_is_slack_message_subtype_present():
    mock_event = {'type': 'message', 'subtype': 'channel_join'}
    result = start_bot.is_slack_message(mock_event)
    assert result is False
