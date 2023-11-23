import gsheets_glossary
import niad_glossary
import os
import utils


def main():
    # 設定ファイルから設定を読み込む
    config = utils.get_config()
    # NIAD用語集一覧を取得する
    niad_glossary_list = niad_glossary.get_niad_glossary(config)
    # 自社用語集の用語URL一覧を取得する
    my_glossary_list = gsheets_glossary.get_my_glossary(config)
    # 用語集一覧を結合する
    deepl_glossary_list = utils.merge_glossary_lists(
        niad_glossary_list, my_glossary_list, config["gsheets_glossary"]["is_priority"]
    )
    # 結合した用語集一覧を出力する
    with open(
        os.path.join(config["output"]["dir"], config["output"]["deepl_glossary"]),
        mode="w",
        encoding="utf-8",
    ) as f:
        glossary = ["\t".join(row) for row in deepl_glossary_list]
        f.write("\n".join(glossary))


if __name__ == "__main__":
    main()
