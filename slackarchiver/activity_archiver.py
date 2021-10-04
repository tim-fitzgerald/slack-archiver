from datetime import datetime
import json
import os
import time

import slack_sdk
import requests

from utils import *

SLACK_USER_TOKEN = os.getenv("ARCHIVER_SLACK_USER_TOKEN")
SLACK_BOT_TOKEN = os.getenv("ARCHIVER_SLACK_BOT_TOKEN")
user_client = slack_sdk.WebClient(token=SLACK_USER_TOKEN)
bot_client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)

DRY_RUN = os.getenv("ARCHIVER_DRY_RUN")

warn_message = """
               It looks like this channel hasn't been used in a while. 
               If there is no further activity in this channel for the next 7 days it will
               be archived. To prevent this channel being archived simply post any message.
                
               If you feel that this is a mistake please reach out to IT.
               """

activity_archive_message = """
                           This channel has not been used in over 45 days and is being archived.
                            
                           If you feel this is a mistake please reach out to IT. 
                           Please note that the contents of archived channels are still searchable. 
                           """

report_channel = "" #Channel ID to send reports to.

SUBTYPES = {"channel_leave", "channel_join", "channel_name"}
with open("ignore_list.json", "r") as f:
    IGNORE_LIST = json.loads(f.read())

warn_list = []
archive_list = []

if DRY_RUN=="False":
    DRY_RUN=False
else:
    DRY_RUN == True

print(DRY_RUN)


def archive(channel_id, message):
    archive_list.append(channel_id)
    if not DRY_RUN:
        print(f"Archiving {channel_id}")
        send_message(channel_id, message)
        response = user_client.channels_archive(channel=channel_id)
        return response
    else:
        print("Dry run: " + channel_id + " would be archived immediately.")
        return {"ok": "true"}


def is_channel_unused(channel_id):
    """
    Using timestamp from `last_message` - determine if the channel meets criteria for being warned or archived.
    """
    stamp = last_message(channel_id)
    if stamp == None:
        print(channel_id + ": No Timestamp")
        return {"ok": "true"}
    inactive_time = datetime.now() - stamp
    if channel_id in IGNORE_LIST:
        print(channel_id + " is ignored")
        return {"ok": "true"}
    elif inactive_time.days >= 45:
        response = archive(channel_id, activity_archive_message)
        return response
    elif inactive_time.days >= 38:
        response = warn(channel_id, warn_message)
        return response
    else:
        print(channel_id + " did not match any criteria")
        return {"ok": "true"}


def last_message(channel_id):
    """
    Find the last message posted by an actual user in the channel history and return the timestamp of that message.
    """
    last_messsage_timestamp = None
    try:
        chan_hist = user_client.conversations_history(
            channel=channel_id, inclusive="0", oldest="0", count="100"
        )
    except:
        return None

    if not chan_hist["messages"]:
        # no messages in channel - so just archive straight away.
        archive(channel_id, activity_archive_message)
        return None
    else:
        for message in chan_hist["messages"]:
            if "subtype" in message and message["subtype"] in SUBTYPES:
                continue
            elif "username" in message and message["username"] == "slackarchiver":
                continue
            else:
                last_messsage_timestamp = datetime.fromtimestamp(float(message["ts"]))
                break
        return last_messsage_timestamp


def report(warn_list, archive_list, count):
    """
    Send a report of warned and archived channels to the #it-notifications channel.
    """
    formatted_message = (
        f"Total Channels: {count} \n\nWarned Channels: {warn_list} \n\nArchived Channels: {archive_list}"
    )
    response = send_message(report_channel, formatted_message)
    return response


def send_message(channel_id, message):
    print("Send message")
    response = bot_client.chat_postMessage(
        channel=channel_id, username="slackarchiver", text=message
    )
    return response


def warn(channel_id, message):
    warn_list.append(channel_id)
    if not DRY_RUN:
        print(f"Warning channel {channel_id}")
        response = send_message(channel_id, message)
        return response
    else:
        print("Dry run: " + channel_id + " would be given a 7 day warning.")
        return {"ok": "true"}


def main():
    channels, count = get_all_channels(bot_client)
    channels = get_channel_ids(channels)
    for id in channels:
        response = is_channel_unused(id)
        time.sleep(1)  # cause rate limiting is a thing

    report(warn_list, archive_list, count)


if __name__ == "__main__":
    main()
