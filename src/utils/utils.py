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
            "deepl_glossary": "deepl_glossary.csv",
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


def list2d_to_dict(list2d: list) -> dict:
    """
    2次元リストを、各行について1列目をキー、2列目をvalueとしたdictに変換する。
    1行目はヘッダー行として無視する。
    """
    converted_dict = {}
    for row in list2d[1:]:
        converted_dict[row[0]] = row[1]
    return converted_dict


def merge_glossary_lists(
    niad_glossary_list: list, my_glossary_list: list, overwrite_niad=True
) -> list:
    """
    NIAD用語集と自社用語集の用語URL一覧を結合する
    """
    if my_glossary_list is None:
        return niad_glossary_list[1:]
    else:
        # NIAD用語集の用語一覧から日本語（1列名）をkey、英訳（2列目）をvalueとしたdictに変換する
        merged_glossary = list2d_to_dict(niad_glossary_list)

        # my_glossary_listの1行目はヘッダー行なので無視する
        for row in my_glossary_list[1:]:
            # niad_glossaryと同様にmy_glossaryも1列目が日本語、2列目が英訳となっている
            if overwrite_niad or row[0] not in merged_glossary:
                # NIAD用語集に存在しない用語の場合、または、上書きフラグがTrueの場合
                if (
                    row[0] in merged_glossary
                    and merged_glossary[row[0]].lower() != row[1].lower()
                ):
                    print(
                        f"{row[0]}の対訳はNIAD用語集に存在しますが、上書きします: {merged_glossary[row[0]]}→{row[1]}"
                    )
                merged_glossary[row[0]] = row[1]
        # 結合した用語集を2次元リストに再変換する
        # 2次元リストは、DeepL用語集の形式に合わせて
        # 1. ヘッダ行なし
        # 2. 各行の内容は [日本語, 英訳, 日本語の言語コード, 英訳の言語コード] となる
        merged_glossary_list = [
            [k, v, "JA", "EN"]
            for k, v in merged_glossary.items()
            if v != "" and v is not None
        ]
        return merged_glossary_list
