import json
from pathlib import Path

import xmltodict

if __name__ == "__main__":
    xml_directory = Path(__file__).parent.parent / "data" / "xml" / "japan"
    save_directory = Path(__file__).parent.parent / "data" / "json" / "japan"

    if not save_directory.exists():
        save_directory.mkdir(parents=True)

    for xml_file in xml_directory.glob("*.xml"):
        with open(xml_file, "r", encoding="utf-8") as f:
            xml_data = f.read()

        json_data = xmltodict.parse(xml_data)
        json_file = save_directory / f"{xml_file.stem}.json"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
