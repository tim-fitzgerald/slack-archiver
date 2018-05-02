## Slack Archiver

This is a script to work through public Slack channels and archive ones over a certain age (60 days by default). 

### Setup
You'll need some tokens. Slack is very much into the whole creating an "app" rather than just giving you some basic API tokens. To set this up
you'll need to go to https://api.slack.com/apps and Create an App. Give it a name and assign it to your workspace. 

Once created - give it the permission scopes required for this script - `channels:history`, `channels:read`, `channels:write`, `bot`. Once scoped for these
permissions you can Install it to your org and this will generate your tokens. Export your tokens as env vars named `SLACK_USER_TOKEN` and `SLACK_BOT_TOKEN` respectively (or dont and edit the scipt for your naming convention) 

## Use
The script needs some variables set for proper use. 

* `SUBTYPES` is a list containing the subtype messages that the script should ignore when trying to find the latest message i.e. by default it will ignore `channel_join`
and `channel_leave` messages 
* `WHITELIST` is a list containing channel ID's that should not be archived even if they meet the criteria for archival. 
* `DRY_RUN` is a flag which when set to `True` will notify the channels of impending archival without actually taking action on them. 
* `age_threshold` is an integer representing the amount of days we want to use to consider a channel inactive - default to 60 days. 