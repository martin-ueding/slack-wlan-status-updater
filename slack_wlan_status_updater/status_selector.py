import collections
import subprocess

Status = collections.namedtuple("Status", ["emoji", "text"])


class StatusSelector:
    def __init__(self, environments):
        self._environments = environments

    def select_status(self) -> Status:
        active_connections = _get_active_connections()
        for environment_name, environment in self._environments.items():
            if environment["network"] in active_connections:
                return Status(environment["emoji"], environment["text"])


def _get_active_connections() -> str:
    result = subprocess.run(
        ["nmcli", "con", "show", "--active"], capture_output=True, check=True
    )
    output = result.stdout.decode()
    return output
