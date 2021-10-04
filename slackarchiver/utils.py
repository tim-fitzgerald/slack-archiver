import json
import os

import slack_sdk

def get_all_channels(client):
    channels = []
    response = client.conversations_list(
        types="public_channel", exclude_archived="true", limit="1000"
    )
    channels.append(response["channels"])
    while response["response_metadata"]["next_cursor"] != "":
        response = client.conversations_list(
            types="public_channel",
            exclude_archived="true",
            limit="1000",
            cursor=response["response_metadata"]["next_cursor"],
        )
        channels.append(response["channels"])
    channels_formatted = []
    for bunch in channels:
        channels_formatted += bunch
    channel_count = len(channels_formatted)
    return channels_formatted, channel_count


def get_channel_ids(channels):
    channel_ids = []
    for ch in channels:
        channel_ids.append(ch["id"])
    print(len(channel_ids))
    return channel_ids

def send_message(channel_id, message):
    print("Send message")
    response = bot_client.chat_postMessage(
        channel=channel_id, username="slackarchiver", text=message
    )
    return response

def warn(channel_id, message):
    print("warn : " + channel_id)
    if not DRY_RUN:
        response = send_message(channel_id, message)
        return response
    else:
        print("Dry run: " + channel_id + " would be given a 7 day warning.")
        return {"ok": "true"}


def archive(channel_id, message):
    print("archive : " + channel_id)
    if not DRY_RUN:
        send_message(channel_id, message)
        response = user_client.channels_archive(channel=channel_id)
        return response
    else:
        print("Dry run: " + channel_id + " would be archived immediately.")
        return {"ok": "true"}