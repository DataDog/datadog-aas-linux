import argparse
import json
import os
import re
from typing import NamedTuple
from urllib.request import urlopen


class Config(NamedTuple):
    name: str
    version_variable: str
    repo_name: str
    major_version_equal_to: int | None


configs = {
    "dotnet": Config(
        name=".NET",
        version_variable="DD_DOTNET_TRACER_VERSION",
        repo_name="dd-trace-dotnet",
        major_version_equal_to=None,
    ),
    "node_v5": Config(
        name="Node.js Tracer v5",
        version_variable="local DD_DEFAULT_NODE_TRACER_VERSION_5",
        repo_name="dd-trace-js",
        major_version_equal_to=5,
    ),
    "java": Config(
        name="Java",
        version_variable="DD_JAVA_TRACER_VERSION",
        repo_name="dd-trace-java",
        major_version_equal_to=None,
    ),
    "php": Config(
        name="PHP",
        version_variable="DD_PHP_TRACER_VERSION",
        repo_name="dd-trace-php",
        major_version_equal_to=None,
    ),
    "python": Config(
        name="Python",
        version_variable="DD_PYTHON_TRACER_VERSION",
        repo_name="dd-trace-py",
        major_version_equal_to=None,
    ),
}


datadog_wrapper_filename = os.path.join(
    os.path.dirname(__file__), "../../", "datadog_wrapper"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"update tracer versions in {datadog_wrapper_filename}"
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
    print(f"current version: {current_version}")

    latest_version = get_latest_version(
        repo_name=config.repo_name, major_version_equal_to=config.major_version_equal_to
    )
    print(f"latest version: {latest_version}")

    if current_version == latest_version:
        print("versions match, nothing to do")
        return

    print(
        f"updating {config.version_variable} from {current_version} to {latest_version}"
    )
    update_version(
        version_variable=config.version_variable,
        current_version=current_version,
        latest_version=latest_version,
    )
    record_update_for_pull_request(
        tracer_name=config.name,
        version_variable=config.version_variable,
        current_version=current_version,
        latest_version=latest_version,
    )


def get_current_version(*, version_variable: str) -> str:
    version_regex = re.compile(version_variable + r"=(\d+\.\d+\.\d+)\s*$")
    with open(datadog_wrapper_filename, "r") as f:
        for line in f:
            line = line.strip()
            if (m := version_regex.match(line)) is not None:
                return m.group(1)

    raise Exception(f"Could not find the current version for {version_variable}")


def get_latest_version(*, repo_name: str, major_version_equal_to: int | None) -> str:
    with urlopen(f"https://api.github.com/repos/datadog/{repo_name}/releases") as r:
        data = json.loads(r.read().decode("utf-8"))

    versions = sorted(
        filter(
            None,
            (
                extract_version(
                    release_entry=entry, major_version_equal_to=major_version_equal_to
                )
                for entry in data
            ),
        ),
        key=version_sort_key,
    )
    return versions.pop()


def extract_version(
    *, release_entry: dict, major_version_equal_to: int | None
) -> str | None:
    tag_name = release_entry["tag_name"]
    match = re.match(r"^v?(\d+\.\d+\.\d+)$", tag_name)
    if match is None:
        return None

    version = match.group(1)

    if major_version_equal_to is None:
        return version

    [major, _, _] = version.split(".")

    if int(major) != major_version_equal_to:
        return None

    return version


def version_sort_key(version: str) -> tuple[int, int, int]:
    parts = tuple(map(int, version.split(".")))
    if len(parts) != 3:
        raise ValueError(f"invalid version: {version}")
    return parts


def update_version(
    *, version_variable: str, current_version: str, latest_version: str
) -> None:
    with open(datadog_wrapper_filename, "r") as f:
        lines = f.readlines()

    with open(datadog_wrapper_filename, "w") as f:
        for line in lines:
            f.write(
                line.replace(
                    f"{version_variable}={current_version}",
                    f"{version_variable}={latest_version}",
                )
            )


def record_update_for_pull_request(
    *,
    tracer_name: str,
    version_variable: str,
    current_version: str,
    latest_version: str,
) -> None:
    output_filename = os.getenv("GITHUB_OUTPUT")
    if output_filename is None:
        raise Exception(
            "Missing GITHUB_OUTPUT environment variable, are we not running in a github workflow?"
        )

    with open(output_filename, "a") as f:
        f.write(f"pr_title=Update {tracer_name} Tracer to {latest_version}\n")
        f.write(
            f"pr_body=Updated {tracer_name} Tracer from {current_version} to {latest_version}\n"
        )


if __name__ == "__main__":
    main()
