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
    :param slack_event: SlackClient instance
    :return: Boolean true if the type is a slack message
    """
    return slack_event["type"] == "message" and \
           'subtype' not in slack_event


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
                if (is_slack_message(event) and
                        bot_is_present_in_channel(slack_client,
                                                  event['channel'])
                ):
                    print(event['text'])
            time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    run()