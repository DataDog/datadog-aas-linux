import argparse
import json
import re
from typing import NamedTuple
from urllib.request import urlopen


class Config(NamedTuple):
    version_variable: str
    repo_name: str


configs = {
    "python": Config(
        version_variable="DD_PYTHON_TRACER_VERSION",
        repo_name="dd-trace-py",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="update tracer versions in datadog_wrapper"
    )
    parser.add_argument(
        "--tracer",
        type=str,
        required=True,
        help="the tracer to update",
        choices=sorted(configs),
    )

    args = parser.parse_args()

    check_version(config=configs[args.tracer])


def check_version(*, config: Config) -> None:
    current_version = get_current_version(version_variable=config.version_variable)

    latest_version = get_latest_version(repo_name=config.repo_name)
    print(f"current version: {current_version}")


def get_current_version(*, version_variable: str) -> str:
    version_regex = re.compile(version_variable + r"=(\d+\.\d+\.\d+)\s*$")
    with open("datadog_wrapper", "r") as f:
        for line in f:
            line = line.strip()
            if (m := version_regex.match(line)) is not None:
                return m.group(1)

    raise Exception(f"Could not find the current version for {version_variable}")


def get_latest_version(*, repo_name: str) -> str:
    with urlopen(f"https://api.github.com/repos/datadog/{repo_name}/releases") as r:
        data = json.loads(r.read().decode("utf-8"))
        print(data)

        # todo: get the version from the latest tag here

        raise NotImplementedError("not implemented")


if __name__ == "__main__":
    main()
