"""
Listens for messages in channels where SlackBot is
if somebody says "@OurSlackBot tutorials" in a channel
with our SlackBot present @OurSlackBot will reply
with Github repo information if the name of the
repository starts with tutorial-
"""
import os
import time

from slackclient import SlackClient

from bot.github_api_wrapper import GithubApiWrapper

POLL_INTERVAL = 1  # seconds between polling from slack


def initialize_slack_client():
    """
    Initializes the SlackClient class and returns it.
    :return: SlackClient instance
    """
    return SlackClient(os.environ['BOT_TOKEN'])


def get_list_of_org_repos():
    """
    Grabs repos that belong to the org from Github API.
    :return: List of tuples containing (name, description, url)
    """
    return GithubApiWrapper.get_org_repos()


def prepare_repo_message(name, desc, url):
    """
    If the repo name starts with 'tutorial-' return a string
    containing the repo metadata, otherwise returns an empty string
    :param name: String Repo name
    :param desc: String Repo description
    :param url: String Repo html url
    :return: String containing repo data, or empty string
    """
    if name.lower().startswith('tutorial-'):
        return (f'*{name}* \n>'
                f'{desc if desc else "Repo has no description"} \n'
                f' {url}' +
                '\n'*5)
    else:
        return ''


def display_org_repos(_slack_client, channel):
    """
    Posts a message containing the name, description, and url
    of repos that belong to the org
    where the repo name starts with 'tutorial-'
    :param _slack_client: SlackClient instance
    :param channel: String ID of Slack channel
    :return: None
    """
    message = f'*{os.environ["GITHUB_ORG"]} repos:*\n'
    repos = get_list_of_org_repos()
    for repo in repos:
        message += prepare_repo_message(*repo)
    post_message_to_channel(_slack_client, channel, message)


def is_bot_is_present_in_channel(_slack_client, slack_channel):
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


def was_bot_direct_mentioned(sc, slack_event):
    """
    Returns true if the message begins with <@{SLACKBOT_ID}>
    :param sc: SlackClient instance
    :param slack_event: Dictionary containing Slack event data
    :return:
    """
    return slack_event['text'].startswith(f'<@{get_bot_id(sc)}>')


def has_bot_received_request(message_text):
    return 'tutorials' in message_text.lower()


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
        if is_bot_is_present_in_channel(_slack_client, s_event['channel']):
            if was_bot_direct_mentioned(_slack_client, s_event):
                if has_bot_received_request(s_event['text']):
                    return True
    return False


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
                    display_org_repos(slack_client, event['channel'])
            time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    run()
