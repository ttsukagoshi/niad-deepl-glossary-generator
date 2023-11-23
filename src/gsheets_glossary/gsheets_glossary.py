# Googleスプレッドシートから自社の用語集を取得する
# 用語集は、次のようなシンプルな構造になっていることを前提としている：
# |  A列  |    B列    |
# |-------|----------|
# |   日   |    英    |　← 1行目はヘッダ行として無視される
# |  顧客  | customer |
# |  ...   |   ...    |

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Delete token.json if SCOPES is modified
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

CREDENTIALS_FILE_PATH = os.path.join(".google", "credentials.json")
TOKEN_FILE_PATH = os.path.join(".google", "token.json")


def authenticate():
    """
    Googleスプレッドシートにアクセスするための認証を行い、認証情報を返す。
    あらかじめ、Google Cloud PlatformでAPIを有効化し、credentials.jsonを取得しておく必要がある。
    https://developers.google.com/sheets/api/quickstart/python
    """
    creds = None
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE_PATH, "w") as token:
            token.write(creds.to_json())
    return creds


def get_my_glossary(config):
    """
    Googleスプレッドシートで管理している自社用語集から、日英対訳の用語集を2次元配列として返す。
    同時に、その2次元配列の内容をCSV形式のテキストとして、glossary_config.jsonで設定した出力先に保存する。
    どちらもヘッダ行付き。
    config: dict - rootのglossary_config.jsonを読み込んだdict
    """
    print("Googleスプレッドシートから自社用語集を取得中...")
    if config["gsheets_glossary"]["spreadsheet_id"] is None:
        # もし設定ファイルでGoogleスプレッドシートIDが指定されていなければ、Noneを返す
        print("設定ファイルでGoogleスプレッドシートIDが指定されていないため、Googleスプレッドシートから自社用語集を取得しませんでした。")
        return None
    else:
        if config["gsheets_glossary"]["sheet_name"] is None:
            raise ValueError("設定ファイルでGoogleスプレッドシートIDを指定した場合は、シート名も指定する必要があります。")
        # Googleスプレッドシートにアクセスするための認証を行う
        creds = authenticate()
        service = build("sheets", "v4", credentials=creds)

        # Sheets APIを使って、Googleスプレッドシートの内容を取得する
        sheet = service.spreadsheets()
        api_result = (
            sheet.values()
            .get(
                spreadsheetId=config["gsheets_glossary"]["spreadsheet_id"],
                range=config["gsheets_glossary"]["sheet_name"],
            )
            .execute()
        )
        sheet_values = api_result.get("values", [])

        if not sheet_values:
            # もし取得したデータが空なら、Noneを返す
            print("指定されたGoogleスプレッドシートにはデータがありませんでした。")
            return None
        else:
            # 空でなければ、取得したデータの1列目と2列目をCSV形式のテキストに変換して、
            # glossary_config.jsonで設定した出力先に保存する。
            # さらに、取得したデータをそのまま返す。

            # 1列目と2列目のみを抽出
            sheet_values_extracted = [row[:2] for row in sheet_values]
            # 1行目のヘッダ行を差し替え
            sheet_values_extracted[0] = ["JA", "EN"]
            # CSV形式のテキストに変換
            csv_text = ""
            for row in sheet_values_extracted:
                csv_text += "\t".join(row) + "\n"
            with open(
                os.path.join(
                    config["output"]["dir"], config["output"]["gsheets_glossary"]
                ),
                "w",
            ) as f:
                f.write(csv_text)
            # 取得したデータをそのまま返す
            print("Googleスプレッドシートから自社用語集を取得しました。")
            return sheet_values_extracted
