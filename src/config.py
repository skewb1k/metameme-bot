import yaml

config_path = "config.yaml"


def read_config() -> dict:
    with open(config_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
