# rootのglossary_config.jsonを読み込む

import json

CONFIG_FILE_PATH = "glossary_config.json"


def get_config() -> dict:
    """
    rootのglossary_config.jsonを読み込んでdictとして返す
    """
    with open(CONFIG_FILE_PATH, mode="r", encoding="utf-8") as f:
        config = json.load(f)
    return config
