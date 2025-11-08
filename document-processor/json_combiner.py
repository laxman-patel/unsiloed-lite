import json
from typing import Dict, Any, List

class JSONCombiner:

    def __init__(self):
        self.combined_data = {}

    def load_and_combine(self, table_file: str, ocr_file: str) -> Dict[str, Any]:
        with open(table_file, 'r', encoding='utf-8') as f:
            table_data = json.load(f)

        with open(ocr_file, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)

        self.combined_data = {
            "tables": self._minimize_tables(table_data),
            "text": self._minimize_ocr(ocr_data)
        }

        return self.combined_data

    def _minimize_tables(self, table_data: Dict) -> List[Dict]:
        if "tables" not in table_data:
            return []

        minimized = []
        for table in table_data["tables"]:
            minimized.append({
                "p": table.get("page"),
                "h": table.get("headers"),
                "d": table.get("data")
            })

        return minimized

    def _minimize_ocr(self, ocr_data: Dict) -> List[Dict]:
        if isinstance(ocr_data, dict):
            if "pages" in ocr_data:
                return [
                    {
                        "p": page.get("page_number"),
                        "t": page.get("text", "").strip()
                    }
                    for page in ocr_data["pages"]
                    if page.get("text", "").strip()
                ]
            elif "text" in ocr_data:
                return [{"t": ocr_data["text"]}]

        return []

    def save_combined(self, output_file: str, minify: bool = True):
        indent = None if minify else 2

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.combined_data, f, indent=indent, ensure_ascii=False)

        print(f"Combined file saved: {output_file}")

    def _calculate_size(self) -> int:
        return len(json.dumps(self.combined_data).encode('utf-8'))

    def _get_file_size(self, filepath: str) -> int:
        try:
            from pathlib import Path
            return Path(filepath).stat().st_size
        except:
            return 0


# Usage
#     combiner = JSONCombiner()

#     # Combine files
#     combiner.load_and_combine("tables.json", "ocr-output.json")

#     # Save minified version
#     combiner.save_combined("combined-output.json", minify=True)
