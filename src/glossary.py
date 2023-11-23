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
    # config.gsheets_glossary.is_priorityの値によって、優先する用語集を決定して結合する
    pass


if __name__ == "__main__":
    main()
