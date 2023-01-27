import argparse
import json
import pathlib
import subprocess
import tomllib
import urllib.request


def get_config() -> dict:
    raw_path = "~/.config/slack-wlan-status-updater/config.toml"
    config_path = pathlib.Path(raw_path).expanduser()
    with open(config_path) as f:
        config = tomllib.load(f)
    return config


def set_status(emoji: str, text: str, token: str) -> None:
    data = {"profile": {"status_emoji": emoji, "status_text": text}}
    url = "https://slack.com/api/users.profile.set"
    headers = {"Content-type": "application/json", "Authorization": f"Bearer {token}"}
    request = urllib.request.Request(url, data=json.dumps(data), headers=headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        print(response.status)


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
    for environment in config["environments"].values():
        if environment["connection"] in active_connections:
            for slack in config["slack"].values():
                set_status(environment["emoji"], environment["text"], slack["token"])
            break


if __name__ == "__main__":
    main()
