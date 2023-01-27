# Update Slack status based on WLAN network

I work from the office and from home, and I switch multiple times in a week. In order for coworkers to keep up with my location, I like to set my status in Slack either as “working from home” or “in the office” with the matching emoji. However, I keep forgetting to update it. And this tool takes care of that for me.

There are various [Slack status update scripts](https://github.com/mivok/slack_status_updater/blob/master/slack_status.sh) to be found online. These are usually a Bash script and provide a command line interface. This is nice, but I want to integrate it with the NetworkManager and also want to make it configurable with a configuration file. On top of that, it seemed like a nice hack project, so I implemented this in Python. Also I have stuck to the Python standard library and not used any external dependencies. This way it is as easy to deploy as I can think of.

It uses the [users.profile.set](https://api.slack.com/methods/users.profile.set) API method of Slack.


## Configuration

Create the following configuration file at `~/.config/slack-wlan-status-updater/config.toml`:

```toml
[slack.work]
token = "…"

[environments.home]
network = "…"
emoji = "haus"
text = "Working from home"

[environments.office]
network = "…"
emoji = "köln"
text = "Office Cologne"
```

You need to fill in the names or UUIDs of the networks that should trigger the environment selection. Only the first one which matches will be used. Add the Slack OAuth tokens that you got from registering your application. You can have multiple Slack instances connected if you want to update more than one.