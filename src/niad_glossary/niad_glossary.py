# NIAD用語集ページをスクレイピングして、日英対訳の用語集をCSV形式のテキストとして返す

import datetime
import json
import os
import re
import requests

TEMP_INDEX_FILE_PATH = os.path.join("temp", "niad_glossary_index.html")
TEMP_INDEX_TIMESTAMP_FILE_PATH = os.path.join(
    "temp", "niad_glossary_index_timestamp.json"
)


def get_html_text(url: str) -> str:
    """
    URLを指定して、そのページのHTMLを取得してテキストとして返す
    """
    r = requests.get(url)
    return r.text


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
    html_text = ""
    html_updated = False
    # tempフォルダに TEMP_INDEX_FILE_PATH が存在するか確認
    if os.path.exists(TEMP_INDEX_FILE_PATH):
        # 存在する場合、最終取得日時を確認
        with open(TEMP_INDEX_TIMESTAMP_FILE_PATH, mode="r", encoding="utf-8") as f:
            timestamp = json.load(f)
        last_index_get = timestamp["last_index_get"]
        # 最終取得日時と現在日時の差が、config["niad_glossary"]["interval_sec"]で指定した秒数未満であれば、
        # TEMP_INDEX_FILE_PATH を読み込む
        now = datetime.datetime.now()
        last = datetime.datetime.strptime(last_index_get, "%Y%m%d%H%M%S")
        interval = datetime.timedelta(seconds=config["niad_glossary"]["interval_sec"])
        if now - last < interval:
            with open(TEMP_INDEX_FILE_PATH, mode="r", encoding="utf-8") as f:
                html_text = f.read()
        else:
            html_text = get_html_text(config["niad_glossary"]["index_url"])
            html_updated = True
    else:
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
    return url_list, html_updated


def get_glossary_details(term_url) -> tuple:
    """
    NIAD用語集の各用語ページのURLからその内容をHTMLテキストとして取得した上で、
    その用語の「日本語」「英語」「意味（日本語）」「意味（英語）」「URL」をこの順のtupleとして返す
    """
    # 用語ページのHTMLテキストを取得
    term_html_text = get_html_text(term_url)
    # 用語ページのHTMLテキストから、目的の各要素を抽出
    glossary_details_pattern = r'<h2 id="jp">(?P<term_ja>[\s\S]*?)<span>[\s\S]*?</h2>\s*?<div class="term_detail">(?P<detail_ja>[\s\S]*?)</div>\s*?<h2 id="en">(?P<term_en>[\s\S]*?)<span>[\s\S]*?</h2>\s*?<div class="term_detail">(?P<detail_en>[\s\S]*?)</div>'
    # glossary_details = re.search(
    #     glossary_details_pattern, term_html_text, re.MULTILINE
    # ).groupdict()
    glossary_details = re.search(glossary_details_pattern, term_html_text, re.MULTILINE)
    print(glossary_details)
    return (
        glossary_details["term_ja"].strip(),
        glossary_details["term_en"].strip(),
        glossary_details["detail_ja"].strip(),
        glossary_details["detail_en"].strip(),
        term_url,
    )
