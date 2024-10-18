from pathlib import Path
from typing import Dict, Generator

import requests
from bs4 import BeautifulSoup
from loguru import logger

BASE_URL = "http://agora.ex.nii.ac.jp/cgi-bin/cps"
TIMEOUT_SECONDS = 10  # リクエストのタイムアウト時間(sec)


def fetch_and_save_ids(report_type: str, output_path: Path) -> None:
    """
    XMLが掲載されたページのIDを取得し、TXTに保存する関数

    Parameters
    ----------
    report_type : str
        データのタイプ（"地上実況図" または "アジア太平洋地上実況図"）
    output_path : Path
        保存先のパス
    """
    with open(output_path, "w") as txtfile:
        for id in fetch_ids(report_type):
            txtfile.write(f"{id}\n")


def donwload_xml(path_to_id_list: Path, output_directory: Path) -> None:
    """
    TXTに保存されたIDをもとにXMLデータをダウンロードし保存する関数

    Parameters
    ----------
    path_to_id_list : Path
        IDが保存されたTXTファイルのパス
    output_directory : Path
        XMLデータの保存先ディレクトリ
    """
    with path_to_id_list.open("r") as txtfile:
        ids = txtfile.read().splitlines()

    for id in ids:
        response = fetch_xml_and_timestamp(id)
        xml_data, target_timestamp = response["xml_data"], response["target_timestamp"]
        if xml_data and target_timestamp:
            xml_file_path = output_directory / f"{target_timestamp}.xml"
            with xml_file_path.open("w") as xmlfile:
                xmlfile.write(xml_data)


def fetch_ids(report_type: str) -> Generator[str, None, None]:
    """
    XMLが掲載されたページのIDを取得するジェネレーター関数

    Parameters
    ----------
    report_type : str
        データのタイプ（"地上実況図" または "アジア太平洋地上実況図"）

    Yields
    ------
    str
        XMLが掲載されたページのID
    """
    page_number = 1
    while True:
        url = f"{BASE_URL}/report_list.pl?type={report_type}&page={page_number}"
        logger.debug(f"Fetching ids from : {url}")
        try:
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()  # HTTPステータスコードのチェック
        except requests.RequestException as e:
            logger.error(f"Failed to fetch page {page_number} for {report_type}: {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        report_table = soup.find("table")

        if not report_table or len(report_table.find_all("tr")) == 0:
            logger.info(f"No more data found for {report_type} on page {page_number}.")
            break

        for report_row in report_table.find_all("tr"):
            yield report_row.get("id")

        page_number += 1


def fetch_xml_and_timestamp(id: str) -> Dict[str, str]:
    """
    指定されたファイル名からXMLデータとタイムスタンプを取得する関数

    Parameters
    ----------
    id : str
        XMLが掲載されたページのID

    Returns
    -------
    Dict[str, str]
        XMLデータと対象日時（TargetDateTime）のタイムスタンプ
    """
    url = f"{BASE_URL}/report_xml.pl?id={id}"
    logger.debug(f"Requesting {url}")

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch XML for {id}: {e}")
        return "", ""

    soup_html = BeautifulSoup(response.content, "html.parser")
    xml_content = soup_html.find("pre").text if soup_html.find("pre") else ""

    if not xml_content:
        logger.warning(f"No XML data found for {id}")
        return "", ""

    soup_xml = BeautifulSoup(xml_content, "xml")
    target_datetime = soup_xml.find("TargetDateTime").text.split("+")[0]
    target_datetime = target_datetime.replace("-", "").replace(":", "")

    return {"xml_data": xml_content, "target_timestamp": target_datetime}


if __name__ == "__main__":
    report_type = "地上実況図"  # "地上実況図" または "アジア太平洋地上実況図"

    # XMLが掲載されたページのIDを取得した結果を保存するファイルのパス
    path_to_ids = Path(__file__).parent.parent / "output" / "japan_ids.txt"
    if not path_to_ids.parent.exists():
        path_to_ids.parent.mkdir(parents=True)

    # XMLデータを保存するディレクトリのパス
    output_dir = Path(__file__).parent.parent / "data" / "xml" / "japan"
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # IDを取得し保存
    fetch_and_save_ids(report_type, path_to_ids)

    # IDをもとにXMLデータをダウンロードし保存
    donwload_xml(path_to_ids, output_dir)
