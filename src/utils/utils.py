# rootのglossary_config.jsonを読み込む

import json
import os

CONFIG_FILE_PATH = "glossary_config.json"


def validate_config(config=None) -> dict:
    """
    configとして与えられたdictを、glossary_config.jsonの形式に合うように
    不足している項目がもしあれば、デフォルト値として追加して返す。
    configが引数として与えられなかった場合は、デフォルト値のdictを返す。
    config: dict - 設定ファイルのdict
    """
    # デフォルト設定値
    default_config = {
        "gsheets_glossary": {
            "spreadsheet_id": None,
            "sheet_name": None,
            "is_priority": True,
        },
        "niad_glossary": {
            "index_url": "https://niadqe.jp/glossary/",
            "interval_sec": 3600,
        },
        "output": {
            "dir": "output",
            "niad_glossary": "niad_glossary.csv",
            "gsheets_glossary": "my_glossary.csv",
        },
    }
    if config is None:
        config = default_config
    else:
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
            else:
                for k, v in value.items():
                    if k not in config[key]:
                        config[key][k] = v
    return config


def get_config() -> dict:
    """
    rootのglossary_config.jsonを読み込んでdictとして返す
    """
    config = {}
    if not os.path.exists(CONFIG_FILE_PATH):
        config = validate_config()
    else:
        with open(CONFIG_FILE_PATH, mode="r", encoding="utf-8") as f:
            config = json.load(f)
    return config
