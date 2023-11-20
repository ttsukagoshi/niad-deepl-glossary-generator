import niad_glossary
import os
import utils


def main():
    # 設定ファイルから設定を読み込む
    config = utils.get_config()
    # NIAD用語集の用語URL一覧を取得する
    niad_term_urls, niad_updated = niad_glossary.extract_glossary_url_list(config)
    niad_terms = ["JA\tEN\tDETAILS_JA\tDETAILS_EN\tURL"]
    """
    if niad_updated:
        # NIAD用語URL一覧が更新された場合、用語集の詳細をあらためて取得する
        for term_url, _ in niad_term_urls:
            niad_terms.append("\t".join(niad_glossary.get_glossary_details(term_url)))
    else:
        print("NIAD用語集の更新はありませんでした。")
    """
    ### 以下、開発用 ###
    for term_url, _ in niad_term_urls:
        niad_terms.append("\t".join(niad_glossary.get_glossary_details(term_url)))
    ### 以上、開発用 ###
    if not os.path.exists(config["output"]["dir"]):
        os.makedirs(config["output"]["dir"])
    with open(
        os.path.join(config["output"]["dir"], config["output"]["niad_glossary"]),
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(niad_terms))


if __name__ == "__main__":
    main()
