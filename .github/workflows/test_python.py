from urllib.request import urlopen
import json

def main() -> None:
    with urlopen("https://api.github.com/repos/datadog/dd-trace-py/releases") as r:
        data = json.loads(r.read().decode("utf-8"))

        print(data)


if __name__ == "__main__":
    main()
