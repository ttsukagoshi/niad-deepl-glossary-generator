# DeepL 用の用語集（CSV）生成ツール（NIAD ＋自社用語集）

独立行政法人大学改革支援・学位授与機構（NIAD）の[用語集（日英）](https://niadqe.jp/glossary/)と、Google スプレッドシートで管理している自社の用語集から、DeepL 翻訳用の用語集を作成するための Python スクリプト。

## 初期設定

### Python のインストール

[Python Releases for Windows | Python.org](https://www.python.org/downloads/windows/)から、Python (>=`v3.10`) をインストールする。

### 本レポジトリをローカル環境に複製

ローカル環境で本レポジトリを複製する。

<img width="684" alt="本レポジトリのトップから、Download ZIPする方法を示したスクリーンショット画像" src="https://github.com/ttsukagoshi/niad-deepl-glossary-generator/assets/55706659/58067455-ba32-4810-adbf-493f92c34061">

### 仮想環境の構築、起動

本レポジトリのトップに移動し、以下のコマンドを実行して`venv`の仮想環境を構築する：

```bash
python -m venv env
```

構築した仮想環境を起動する：

```bash
# Windows
env\Scripts\activate

# macOS, Linux
source env/bin/activate
```

仮想環境内で、必要なパッケージをインストールする：

```bash
pip install -r requirements.txt
```

### Google スプレッドシートを参照するための認証情報を取得

[Python quickstart | Google for Developers](https://developers.google.com/sheets/api/quickstart/python)の手順に沿って、Python で Google スプレッドシートにアクセスするための準備をする。上記ページの中段にある`credentials.json`は、本レポジトリにある`.google`フォルダに格納する。

### 設定ファイル`glossary_config.json`の作成

以下の設定ファイルをコピーして `glossary_config.json` としてレポジトリのトップに保存する。
コメントを参照しながら、各要素の値は適宜調整する。

```jsonc
{
  "gsheets_glossary": {
    "spreadsheet_id": "", // 自社用語集のスプレッドシートID
    "sheet_name": "glossary", // 自社用語集のシート名
    "is_priority": true // 自社用語集を優先するかどうか。trueであれば、NIAD用語集に同じ用語があっても自社用語集の対訳を優先する
  },
  "niad_glossary": {
    "index_url": "https://niadqe.jp/glossary/", // NIAD用語集のトップページURL
    "interval_sec": 86400 // 新たにNIAD用語集にアクセスするまでの間隔（秒）
  },
  "output": {
    "dir": "output", // 出力先ディレクトリ
    "niad_glossary": "niad_glossary.csv", // NIAD用語集の出力CSVファイル名
    "gsheets_glossary": "my_glossary.csv", // 自社用語集の出力CSVファイル名
    "deepl_glossary": "deepl_glossary.csv" // 最終的に出力するDeepL用の出力CSVファイル名
  }
}
```

## 自社用語集の準備

Google スプレッドシートにて、以下のような形式で自社用語集を管理することも想定できる：

| A 列 | B 列     |
| ---- | -------- |
| 日   | 英       |
| 顧客 | customer |
| ...  | ...      |

> 1 行目（「日」「英」）はヘッダ行として無視される

この際、必ず A 列に日本語を、B 列に英語を入力すること。
作成したスプレッドシートの ID を、`glossary_config.json`の`gsheets_glossary.spreadsheet_id`に指定する。

NIAD 用語集の用語を、自社用語集で別の英訳に置き換えたい場合もある。このようなときは`glossary_config.json`の`gsheets_glossary.is_priority`を`true`に設定する。

## 実行する

仮想環境を起動した状態で、以下のコマンドを実行する：

```bash
python src/glossary.py
```
