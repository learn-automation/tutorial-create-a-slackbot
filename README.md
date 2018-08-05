# Create a SlackBot

This will be a short tutorial to show you how to create SlackBots.  The SlackBot will listen to a particular Slack channel and preform actions if specific statements are made in the chat.

## Getting Started

To follow along with this tutorial there are a couple steps we must take before getting to the fun part.

### Prerequisites

Before we can write any code, we must create a [Slack App](https://api.slack.com/apps/new).

After the Slack App has been created, add a bot user by clicking "Bot" then "Add a Bot User".

Click on OAuth & Permissions, and add the permissions your app will use (`bot` should be present at this point). For the bot I am creating for this tutorial I will add the following permissions:
`channels:read`
`channels:write`

Next, we need to install the new Slack app into the workspace by clicking Basic Information -> Install your app to your workspace 

Then we need to save the credentials from the Basic Information page:
`Client ID`
`Client Secret`

The final credential we need can be found by clicking Install App (in the navigation bar on the left):
`Bot User OAuth Access Token`

### Building the bot

#### Defining the project structure & dependencies

1. Create a new project using your preferred IDE (I use [PyCharm](https://www.jetbrains.com/pycharm/download/)).
2. Create a new file at the root of your project called `setup.py`.
We will use this file to list the third-party Python dependencies we need to start developing a new SlackBot.
    1. ```python
        #setup.py
       from setuptools import setup
    
       version = '1.0.0'
       
       requirements = [
          'requests',
          'slackclient'
       ]
       
       dev_requirements = [
            'pytest'
       ] 
       
       setup(name='YOUR_SLACKBOT_NAME',
            version=version,
            description='SlackBot that listens to channels and takes action on them',
            author='YOUR_NAME',
            author_email='YOUR_EMAIL',
            url='LINK_TO_YOUR_GIT_REPO',
            install_requires=requirements,
            extras_require={'dev': dev_requirements},
            packages=['bot'],
       )
       ```
    2. To learn more about setup.py read [the docs](https://docs.python.org/3/distutils/setupscript.html) and see [this readme](https://github.com/learn-automation/tutorial-jira-api-wrapper/blob/master/README.md)
3. Create a new directory called "bot"
4. From the root of your project, run the following command: `pip install -e .[dev]`

#### Iteration 1: Subscribe to Slack Channel

The first goal we should set for ourselves is giving the bot the ability to read messages.
1. Invite your bot to a Slack channel - I use #slack-bot-testing
2. Set a new environment variable `BOT_TOKEN` with the value from `Bot User OAuth Access Token`
3. Create `./bot/start_bot.py`
    1. ```python
       # start_bot.py
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
           slack_bot_user = _slack_client.api_call("auth.test")["user_id"]
           channel_info = get_channel_info(_slack_client, slack_channel)
           if 'channel' in channel_info:
               if 'members' in channel_info['channel']:
                   if slack_bot_user in channel_info['channel']['members']:
                       return True
           return False
       
       
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
       ```
       
1. Now that we have written some code, we need to write some tests.  Create a `tests` directory and add `test_start_bot.py` to it. 
    1. ```python
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
    
       ```

#### Iteration 2: Make bot respond to direct mentions that match our business logic
Now that our Slackbot is able to listen to a channel, let's have it reply with a specific message when our SlackBot is called. 
1. Let's add some new functions to `start_bot.py`:
    1. ```python
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
        ```
2. Now we need to modify the `run` function:
    ```python
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
    ```