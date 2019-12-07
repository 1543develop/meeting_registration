import json
import os

CONFIG_PY_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG_SECRETS = CONFIG_PY_PATH + "/config_secrets.json"


class ConfigSecrets:
    def __init__(self):
        with open(CONFIG_SECRETS, "r", encoding="utf-8") as file:
            self.res = json.loads(file.read())

    def __getitem__(self, item):
        return self.res[item]


if __name__ == '__main__':
    print(ConfigSecrets()["django_secret_key"])
