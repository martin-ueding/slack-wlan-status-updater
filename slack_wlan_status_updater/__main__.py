import argparse
import datetime
import pathlib
import time
import tomllib

from .status_setter import InterceptingSlackStatusSetterDecorator
from .status_setter import MultiStatusSetter
from .status_setter import SlackStatusSetter
from .status_setter import StatusSetter
from .status_selector import StatusSelector


class MainLoop:
    def __init__(
        self,
        status_selector: StatusSelector,
        status_setter: StatusSetter,
        poll_minutes: int,
    ):
        self._status_selector = status_selector
        self._status_setter = status_setter
        self._poll_minutes = poll_minutes

    def run(self) -> None:
        while True:
            emoji, text = self._status_selector.select_status()
            expiration = datetime.datetime.combine(
                datetime.date.today(), datetime.time(23, 59, 59)
            )
            self._status_setter.set_status(emoji, text, expiration)
            time.sleep(self._poll_minutes * 60)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--poll-minutes",
        type=float,
        default=5,
        help="Poll interval in minutes. Default: %(default)d",
    )
    options = parser.parse_args()

    config = get_config()
    status_selector = build_status_selector(config)
    status_setter = build_status_setter(config)
    main_loop = MainLoop(status_selector, status_setter, options.poll_minutes)

    main_loop.run()


def get_config() -> dict:
    raw_config_path = "~/.config/slack-wlan-status-updater/config.toml"
    config_path = pathlib.Path(raw_config_path).expanduser()
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    return config


def build_status_selector(config: dict) -> StatusSelector:
    return StatusSelector(config["environments"])


def build_status_setter(config: dict) -> StatusSetter:
    slack_status_setters = [
        SlackStatusSetter(name, slack["token"]) for name, slack in config["slack"].items()
    ]
    interceptors = [
        InterceptingSlackStatusSetterDecorator(slack_status_setter)
        for slack_status_setter in slack_status_setters
    ]
    multi = MultiStatusSetter(interceptors)
    return multi


if __name__ == "__main__":
    main()
