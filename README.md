## Slack Archiver

This is a script to work through public Slack channels and archive ones over a certain age (60 days by default). 

### Setup
You'll need some tokens. Slack is very much into the whole creating an "app" rather than just giving you some basic API tokens. To set this up
you'll need to go to https://api.slack.com/apps and Create an App. Give it a name and assign it to your workspace. 

Once created - give it the permission scopes required for this script - `channels:history`, `channels:read`, `channels:write`, `bot`. Once scoped for these
permissions you can Install it to your org and this will generate your tokens. Export your tokens as env vars named `SLACK_USER_TOKEN` and `SLACK_BOT_TOKEN` respectively. 

Modify the file `ignore_list.json` to be a JSON array of channel ID's you want the tool to ignore.

## Use
First you'll need to build the container with `docker build . -t slackarchiver:<version>`.

You'll then need to create a `.env` file in the root of this repo and populate the following variables.

```
ARCHIVER_SLACK_USER_TOKEN=xoxp-1234567890
ARCHIVER_SLACK_BOT_TOKEN=xoxb-0987654321
ARCHIVER_DRY_RUN=True
```

When `ARCHIVER_DRY_RUN` is set to `True` the tool will run in a silent mode, not notifying or arching any channels. It will send a single report to the notifications channel with a list of channels to be archived or warned. 

Run the tool with the defaults for a silent run with:

`docker run -it --env-file ./.env --name slackarchiver slackarchiver:<version>`

To run the tool and perform actual archiving - override the `ARCHIVER_DRY_RUN` variable with:

`docker run -it --env-file ./.env -e ARCHIVER_DRY_RUN=False --name slackarchiver slackarchiver:latest`