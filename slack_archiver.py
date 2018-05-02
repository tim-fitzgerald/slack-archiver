import os
import requests
import json
from datetime import timedelta, datetime
import sys
import time

##### SLACK VARIABLES #####
# Two headers are needed due to the user token being needed to get channel history
# and bot user needed to post the notification and close the channel
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_uri = "https://slack.com/api/"

headers_user = {
    "Authorization" : "Bearer " + SLACK_USER_TOKEN,
    "Content-type" : "application/json"
}

headers_bot = {
    "Authorization" : "Bearer " + SLACK_BOT_TOKEN,
    "Content-type" : "application/json"
}

###########################
###########################

SUBTYPES = {'channel_leave', 'channel_join'}
WHITELIST = []
DRY_RUN = True

unused_channels = []
age_threshold = 60 #days
age_threshold_secs = age_threshold / 86400

def get_channels(base_uri, my_headers):
    channel_ids = []
    api_endpoint = "channels.list"
    req_url = slack_uri + api_endpoint
    parameters = {'exclude_archived': 1}
    response = requests.get(req_url, headers=my_headers, params=parameters)
    response = response.json()
    channels = response["channels"]
    return channels

def channel_activity(base_uri, my_headers, my_channel):
    # First check if theres any messages at all in the channel - if not mark it for archival
    # Otherwise loop over the messages until we find a message posted by an actual user
    # and get the timestamp for that message - that timestamp is passed to the channel_unused function
    # to assess whether its inactive or not
    last_messsage_timestamp = None
    api_endpoint = "channels.history"
    req_url = base_uri + api_endpoint
    chan_id = my_channel['id']
    parameters = {'channel': chan_id, 'inclusive': 0, 'oldest': 0, 'count': 15}
    response = requests.post(req_url, headers=my_headers, params=parameters)
    chan_hist = response.json()

    if 'messages' not in chan_hist:
        #no messages in channel
        unused_channels.append(chan_id)
        return None
    else:
        for message in chan_hist['messages']:
            if 'subtype' in message and message['subtype'] in SUBTYPES:
                continue
            elif 'username' in message and message['username'] == 'slack_archiver':
                continue
            else:
                last_messsage_timestamp = datetime.fromtimestamp(float(message['ts']))
                break
        return last_messsage_timestamp

def channel_unused(my_id, stamp):
    if stamp == None:
        return None
    else:
        inactive_time = datetime.now() - stamp
        if inactive_time.days > 60:
            unused_channels.append(my_id)

def send_message(base_uri, my_headers, my_id):
    payload = {"channel": my_id, "username": "slack_archiver", "text": "This channel has not been used in over 60 days and will be archived. If you feel this is a mistake please reach out in #it-help"}
    if DRY_RUN == True:
        payload['text'] = "This is a dry run of a tool to auto-archive unused channels in Slack. This channel has not been used in over 60 days and will be archived on next run. If you feel this is a mistake please reach out in #it-help"
    payload_json = json.dumps(payload)
    api_endpoint = 'chat.postMessage'
    req_url = base_uri + api_endpoint
    response = requests.post(req_url, headers=my_headers, data=payload_json)
    print (response.json())
   
def archive_channel(base_uri, my_headers, channels_list):
    api_endpoint = channels.archive
    req_url = base_uri + api_endpoint
    for channel in channels_list:
        payload = {"channel": channel}
        response = requests.post(req_url, headers=my_headers)


def main():
    channels = get_channels(slack_uri, headers_user)

    for channel in channels:
        print ('.', end='', flush=True)
        if channel['id'] in WHITELIST:
            continue
        last_timestamp = channel_activity(slack_uri, headers_user, channel)
        channel_unused(channel['id'], last_timestamp)
        time.sleep(1.0)

    for channel in unused_channels:
        print ('.', end='', flush=True)
        send_message(slack_uri, headers_bot, channel)
    
    if DRY_RUN != True:
        print ('.', end='', flush=True)
        archive_channel(slack_uri, headers_user, unused_channels)

    #for i in unused_channels:
        #print (i)
    
if __name__ == "__main__":
    main()