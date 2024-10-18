# detect-front-public sub/xml

- `sub/*`は独立ブランチです
- 本ブランチ`sub/xml`では、気象庁が発表しているxmlファイル形式の地上実況図をダウンロードし、各気象要素を抽出するプログラムを提供します

## Environment Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Usage

### `scripts/downloader.py`
- 概要：[気象庁防災情報XMLデータベース](http://agora.ex.nii.ac.jp/cps/weather/report/)から、XMLファイルをダウンロードする。
- `fetch_and_save_ids`関数で、ダウンロード対象のXMLファイルのIDを取得できる
    - 取得結果は、変数`path_to_ids`で指定したテキストファイルに保存される
    - ダウンロードしたくないIDがある場合は、テキストファイルから削除する
- `download_xml`関数で、XMLファイルをダウンロードする
    - 上記で取得したIDを元に、XMLファイルをダウンロードする
    - ダウンロード先は、変数`output_dir`で指定したディレクトリ

### `scripts/xml_to_json.py`
- 概要：ダウンロードしたXMLファイルをJSONファイルに変換する
- `xml_to_json`関数で、XMLファイルをJSONファイルに変換する
    - 変数`xml_directory`で指定したディレクトリ内のすべてのXMLファイルを変換し、変数`save_directory`で指定したディレクトリにJSONが保存される
