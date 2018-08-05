"""
Listens for messages in channels where SlackBot is
a member and prints the message to Stdout
"""
import os
import time

from slackclient import SlackClient

POLL_INTERVAL = 1  # seconds between polling from slack


def initialize_slack_client():
    """
    Initializes the SlackClient class and returns it.
    :return: SlackClient instance
    """
    return SlackClient(os.environ['BOT_TOKEN'])


def bot_is_present_in_channel(_slack_client, slack_channel):
    """
    Checks if bot is a member in the slack_channel.
    :param _slack_client: SlackClient instance
    :param slack_channel: String Slack channel ID
    :return: Boolean true if bot exists in channel
    """
    slack_bot_user = get_bot_id(_slack_client)
    channel_info = get_channel_info(_slack_client, slack_channel)
    if 'channel' in channel_info:
        if 'members' in channel_info['channel']:
            if slack_bot_user in channel_info['channel']['members']:
                return True
    return False


def get_bot_id(_slack_client):
    """
    Returns the ID of the SlackBot.
    :param _slack_client: SlackClient instance
    :return: String SlackBot's ID
    """
    return _slack_client.api_call("auth.test")["user_id"]


def get_channel_info(sc, channel):
    """
    Returns the channel info.
    :param sc: SlackClient instance
    :param channel: String Slack channel ID
    :return: Dict containing channels.info response
    """
    return sc.api_call(
        "channels.info",
        channel=channel
    )


def is_slack_message(slack_event):
    """
    Returns true if the event type is a message and not a subtype.
    Subtypes are events like a user joining a channel.
    :param slack_event: Dictionary containing Slack event data
    :return: Boolean true if the type is a slack message
    """
    return (slack_event["type"] == "message" and
            'subtype' not in slack_event)


def bot_was_direct_mentioned(sc, slack_event):
    """
    Returns true if the message begins with <@{SLACKBOT_ID}>
    :param sc: SlackClient instance
    :param slack_event: Dictionary containing Slack event data
    :return:
    """
    return slack_event['text'].startswith(f'<@{get_bot_id(sc)}>')


def bot_received_request(_slack_client, s_event):
    """
    Returns true if bot was mentioned at the beginning of
    a message in a channel the bot is in.
    :param _slack_client: SlackClient instance
    :param s_event: Dictionary containing Slack event data
    :return: Boolean true if bot was mentioned and
             is a member in the channel
    """
    if is_slack_message(s_event):
        if bot_is_present_in_channel(_slack_client, s_event['channel']):
            if bot_was_direct_mentioned(_slack_client, s_event):
                return True
    return False


def repeats_message_back_to_user(_slack_client, slack_event):
    """
    Repeats the message back to the user
    :param _slack_client: SlackClient instance
    :param slack_event: Dictionary containing Slack event data
    :return: None
    """
    post_message_to_channel(_slack_client, slack_event['channel'], slack_event['text'])


def post_message_to_channel(sc, channel, message, thread=None, broadcast=None):
    """
    Posts message to Slack channel
    :param sc: SlackClient instance
    :param channel: String Slack channel id
    :param message: String message to send
    :param thread: String Timestamp of thread (event['ts']) or event['thread_ts'])
    :param broadcast: Boolean broadcasts threaded message to main channel
    :return: None
    """
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message,
        thread_ts=thread,
        reply_broadcast=broadcast
    )


def run():
    """
    Runs the SlackBot
    :return: None
    """
    slack_client = initialize_slack_client()
    if slack_client.rtm_connect(
            with_team_state=False,
            auto_reconnect=True
    ):
        while True:
            print('listening')
            for event in slack_client.rtm_read():
                if bot_received_request(slack_client, event):
                    repeats_message_back_to_user(slack_client, event)
            time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    run()
