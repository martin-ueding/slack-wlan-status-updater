import argparse
import datetime
import json
import pathlib
import subprocess
import tomllib
import urllib.request


def get_config() -> dict:
    raw_path = "~/.config/slack-wlan-status-updater/config.toml"
    config_path = pathlib.Path(raw_path).expanduser()
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)
    return config


def set_status(emoji: str, text: str, token: str) -> None:
    midnight = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59, 59))
    data = {"profile": {"status_emoji": f":{emoji}:", "status_text": text, "status_expiration": midnight.timestamp()}}
    url = "https://slack.com/api/users.profile.set"
    headers = {"Content-type": "application/json", "Authorization": f"Bearer {token}"}
    request = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        assert response.status == 200
        response_data = json.loads(response.read().decode())
        assert response_data["ok"], response_data


def get_active_connections() -> str:
    result = subprocess.run(
        ["nmcli", "con", "show", "--active"], capture_output=True, check=True
    )
    output = result.stdout.decode()
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    options = parser.parse_args()

    config = get_config()
    active_connections = get_active_connections()
    for environment_name, environment in config["environments"].items():
        if environment["network"] in active_connections:
            for slack_name, slack in config["slack"].items():
                print(f"Setting status according to environment “{environment_name}” for Slack workspace “{slack_name}”.")
                set_status(environment["emoji"], environment["text"], slack["token"])
            break


if __name__ == "__main__":
    main()
