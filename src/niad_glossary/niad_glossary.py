# NIAD用語集ページをスクレイピングして、日英対訳の用語集をCSV形式のテキストとして返す

import datetime
import json
import os
import re
import requests

TEMP_DIR_PATH = "temp"
TEMP_INDEX_FILE_PATH = os.path.join(TEMP_DIR_PATH, "niad_glossary_index.html")
TEMP_INDEX_TIMESTAMP_FILE_PATH = os.path.join(
    TEMP_DIR_PATH, "niad_glossary_index_timestamp.json"
)
TEMP_TERMS_DIR_PATH = os.path.join(TEMP_DIR_PATH, "niad_terms")
TEMP_TERMS_FILE_PATH = os.path.join(TEMP_TERMS_DIR_PATH, "[[page_id]].html")


def get_html_text(url: str) -> str:
    """
    URLを指定して、そのページのHTMLを取得してテキストとして返す
    """
    r = requests.get(url)
    return r.text


def get_local_html_text(filepath: str) -> str:
    """
    ローカルのHTMLファイルを読み込んでテキストとして返す
    """
    with open(filepath, mode="r", encoding="utf-8") as f:
        return f.read()


def extract_glossary_url_list(config) -> tuple:
    """
    NIAD用語集のインデックスページのHTMLテキストから、
    記載されている用語集のURLを (URL, 用語) のtupleとして抽出しそのリストを返す。
    NIAD用語集ページへの過度のアクセスを避けるため、一度アクセスするとHTMLテキストのコピーと
    取得日時がtempフォルダ内に記録され、次回実行時に、前回取得日時からの間隔が
    glossary_config.json で指定した間隔（秒）未満であれば、
    サイトにアクセスせず代わりにtempフォルダ内のHTMLテキストを読み込む。
    config: dict - rootのglossary_config.jsonを読み込んだdict
    return: tuple - (URL, 用語) のtupleのリストと、サイトにアクセスして更新したかどうかのbool値
    """
    print("NIAD用語集のインデックスページから、各用語集のURLを取得中...")

    html_text = ""
    html_updated = False
    # tempフォルダに TEMP_INDEX_FILE_PATH が存在するか確認
    if os.path.exists(TEMP_INDEX_FILE_PATH):
        # TEMP_INDEX_FILE_PATHが存在する場合、最終取得日時を確認
        print(f"{TEMP_INDEX_FILE_PATH} が存在します。最終取得日時を確認します。")
        with open(TEMP_INDEX_TIMESTAMP_FILE_PATH, mode="r", encoding="utf-8") as f:
            timestamp = json.load(f)
        last_index_get = timestamp["last_index_get"]
        # 最終取得日時と現在日時の差が、config["niad_glossary"]["interval_sec"]で指定した秒数未満であれば、
        # TEMP_INDEX_FILE_PATH を読み込む
        now = datetime.datetime.now()
        last = datetime.datetime.strptime(last_index_get, "%Y%m%d%H%M%S")
        interval = datetime.timedelta(seconds=config["niad_glossary"]["interval_sec"])
        if now - last < interval:
            print(f"最終取得日時は{last}であることから、サイトにはアクセスせず、{TEMP_INDEX_FILE_PATH} を読み込みます。")
            with open(TEMP_INDEX_FILE_PATH, mode="r", encoding="utf-8") as f:
                html_text = f.read()
        else:
            print(f"最終取得日時は{last}であることから、サイトにアクセスして{TEMP_INDEX_FILE_PATH} を更新します。")
            html_text = get_html_text(config["niad_glossary"]["index_url"])
            html_updated = True
    else:
        # TEMP_INDEX_FILE_PATHが存在しない場合、サイトにアクセスしてHTMLテキストを取得
        print(f"{TEMP_INDEX_FILE_PATH} が存在しません。サイトにアクセスしてHTMLテキストを取得します。")
        if not os.path.exists(TEMP_DIR_PATH):
            os.makedirs(TEMP_DIR_PATH)
        html_text = get_html_text(config["niad_glossary"]["index_url"])
        html_updated = True

    # 最新のHTMLを読み込んだ場合は、TEMP_INDEX_FILE_PATH と TEMP_INDEX_TIMESTAMP_FILE_PATH を更新
    if html_updated:
        with open(TEMP_INDEX_FILE_PATH, mode="w", encoding="utf-8") as f:
            f.write(html_text)
        # 最終取得日時を同じtempフォルダの niad_glossary_index_timestamp.json に保存
        timestamp = {"last_index_get": datetime.datetime.now().strftime("%Y%m%d%H%M%S")}
        with open(
            TEMP_INDEX_TIMESTAMP_FILE_PATH,
            mode="w",
            encoding="utf-8",
        ) as f:
            json.dump(timestamp, f, indent=4)
    # 用語集の目次から、日本語の用語集の部分を抽出
    glossary_ja_index_pattern = (
        r'<h2 id="term_jp">用語一覧（日本語）</h2>[\s\S]*?<h2 id="term_en">Terms（English）</h2>'
    )
    glossary_ja = re.search(glossary_ja_index_pattern, html_text, re.MULTILINE).group(0)
    # 日本語の用語集部分に対して、用語のブロック（あいうえお順）を抽出
    glossary_term_block_pattern = r'<ul class="term_list">[\s\S]*?</ul>'
    term_blocks_list = re.findall(
        glossary_term_block_pattern, glossary_ja, re.MULTILINE
    )
    # 各ブロックから、用語とURLを抽出
    url_list = []
    for term_block in term_blocks_list:
        url_pattern = r'<li>\s*?<a href="(?P<url>https://niadqe\.jp/glossary/\S*?/)">(?P<term>\S*?)</a>\s*?</li>'
        url_list += re.findall(url_pattern, term_block, re.MULTILINE)
    print("各用語集のURL取得完了")
    return url_list, html_updated


def get_glossary_details(term_url, local=False) -> tuple[str]:
    """
    NIAD用語集の各用語ページのURLからその内容をHTMLテキストとして取得した上で、
    その用語の「日本語」「英語」「意味（日本語）」「意味（英語）」「URL」をこの順のtupleとして返す
    """
    print(f"{term_url} の詳細を{'保存済みのローカルファイル' if local else '用語集サイト'}から取得中...")
    # 用語ページのHTMLテキストを保存した/する一時ファイルのパスを定義
    temp_terms_file_path = TEMP_TERMS_FILE_PATH.replace(
        "[[page_id]]", term_url.split("/")[-2]
    )
    # もしローカルに保存するためのディレクトリが存在しなければ、作成
    if not os.path.exists(TEMP_TERMS_DIR_PATH):
        os.makedirs(TEMP_TERMS_DIR_PATH)

    # 用語ページのHTMLテキストを取得
    term_html_text = (
        get_html_text(term_url)
        if not local
        else get_local_html_text(temp_terms_file_path)
    )
    if not local:
        # もしサイトから取得した場合は、一時ファイルを保存
        with open(temp_terms_file_path, mode="w", encoding="utf-8") as f:
            f.write(term_html_text)

    # 用語ページのHTMLテキストから、目的の各要素を抽出
    glossary_details_pattern = r'<h2 id="jp">(?P<term_ja>[\s\S]*?)<span>[\s\S]*?</h2>\s*?<div class="term_detail">(?P<detail_ja>[\s\S]*?)</div>(\s*?<h2 id="en">(?P<term_en>[\s\S]*?)<span>[\s\S]*?</h2>\s*?<div class="term_detail">(?P<detail_en>[\s\S]*?)</div>)?'
    glossary_details = re.search(
        glossary_details_pattern, term_html_text, re.MULTILINE
    ).groupdict()
    print(f"{term_url} の詳細取得完了")
    return (
        glossary_details["term_ja"].strip().replace("\r", " ").replace("\n", " ")
        if glossary_details["term_ja"] is not None
        else "",
        glossary_details["term_en"].strip().replace("\r", " ").replace("\n", " ")
        if glossary_details["term_en"] is not None
        else "",
        glossary_details["detail_ja"].strip().replace("\r", " ").replace("\n", " ")
        if glossary_details["detail_ja"] is not None
        else "",
        glossary_details["detail_en"].strip().replace("\r", " ").replace("\n", " ")
        if glossary_details["detail_en"] is not None
        else "",
        term_url,
    )


def get_niad_glossary(config) -> list[str]:
    """
    NIAD用語集から、日英対訳の用語集を2次元配列として返す。
    同時に、その2次元配列の内容をCSV形式のテキストとして、glossary_config.jsonで設定した出力先に保存する。
    どちらもヘッダ行付き。
    config: dict - rootのglossary_config.jsonを読み込んだdict
    """
    # NIAD用語集のインデックスページから、各用語集のURLを取得
    niad_term_urls, niad_updated = extract_glossary_url_list(config)

    # ヘッダ行を定義
    niad_terms = ["JA\tEN\tDETAILS_JA\tDETAILS_EN\tURL"]

    # 用語集の各ページについて、ローカルに保存済みの一時ファイルから読み込むか、新規に取得するかのフラグ
    get_local = False if niad_updated else True

    # 用語集の各ページから詳細を取得
    for term_url, _ in niad_term_urls:
        niad_terms.append("\t".join(get_glossary_details(term_url, local=get_local)))

    # 用語集の詳細をCSV形式のテキストとして出力
    if not os.path.exists(config["output"]["dir"]):
        os.makedirs(config["output"]["dir"])
    with open(
        os.path.join(config["output"]["dir"], config["output"]["niad_glossary"]),
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(niad_terms))

    # 用語集の詳細を2次元配列として返す
    return [term.split("\t") for term in niad_terms]
