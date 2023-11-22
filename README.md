# niad-glossary

NIAD の用語集（日英）と自社の用語集から、DeepL 用の用語集を作成する。

## 初期設定

## 使い方

### 設定ファイル `glossary_config.json`

```jsonc
{
  "gsheets_glossary": {
    "spreadsheet_id": "", // 自社用語集のスプレッドシートID
    "is_priority": true // 自社用語集を優先するかどうか。trueであれば、NIAD用語集に同じ用語があっても自社用語集の対訳を優先する
  },
  "niad_glossary": {
    "index_url": "https://niadqe.jp/glossary/", // NIAD用語集のトップページURL
    "interval_sec": 86400 // 新たにNIAD用語集にアクセスするまでの間隔（秒）
  },
  "output": {
    "dir": "output", // 出力先ディレクトリ
    "niad_glossary": "niad_glossary.csv" // NIAD用語集の出力CSVファイル名
  }
}
```
