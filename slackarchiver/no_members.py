import json
import os
import time

import slack_sdk
from utils import *

SLACK_USER_TOKEN = os.getenv("ARCHIVER_SLACK_USER_TOKEN")
SLACK_BOT_TOKEN = os.getenv("ARCHIVER_SLACK_BOT_TOKEN")
user_client = slack_sdk.WebClient(token=SLACK_USER_TOKEN)
bot_client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)


def no_member_channels():
    offenders = []
    channels = get_all_channels()
    for ch in channels:
        if ch["num_members"] == 0:
            offenders.append(ch["id"])
    return offenders


def send_message(channel_id, message):
    print("Send message")
    response = bot_client.chat_postMessage(
        channel=channel_id, username="slackarchiver", text=message
    )
    return response


def archive(channel_id):
    message = """
    This channel has 0 members and it is being archived! The contents of the channel
    will still be browsable.
    """
    send_message(channel_id, message)
    response = user_client.channels_archive(channel=channel_id)
    return response


def main():
    channels = no_member_channels()
    for chan_id in channels:
        resp = archive(chan_id)
        print(chan_id + ": " + str(resp["ok"]))
        time.sleep(1.0)


if __name__ == "__main__":
    main()
