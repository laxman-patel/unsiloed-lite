import pdfplumber
import json
from typing import List, Dict, Any

class TableExtractor:

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.tables = []

    def extract_tables(self) -> List[Dict[str, Any]]:
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()

                for table_num, table in enumerate(tables, start=1):
                    if table and len(table) > 1:
                        clean_table = self._convert_to_json(table, page_num, table_num)
                        if clean_table:
                            self.tables.append(clean_table)

        return self.tables

    def _convert_to_json(self, table: List[List], page: int, table_num: int) -> Dict:
        headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(table[0])]

        rows = []
        for row in table[1:]:
            if not any(row):
                continue

            row_data = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else None
                row_data[header] = self._clean_value(value)

            rows.append(row_data)

        if not rows:
            return None

        return {
            "page": page,
            "table": table_num,
            "headers": headers,
            "data": rows
        }

    def _clean_value(self, value: Any) -> Any:
        if value is None or str(value).strip() == "":
            return None

        cleaned = str(value).strip().replace('\n', ' ')

        try:
            num_str = cleaned.replace(',', '').replace('$', '').replace('€', '').replace('£', '')

            if num_str.startswith('(') and num_str.endswith(')'):
                num_str = '-' + num_str[1:-1]

            if '.' in num_str:
                return float(num_str)
            else:
                return int(num_str)
        except:
            return cleaned

    def save_json(self, output_path: str):
        output = {
            "source": self.pdf_path,
            "total_tables": len(self.tables),
            "tables": self.tables
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Extracted {len(self.tables)} tables")
        print(f"Saved to: {output_path}")


# usage
# if __name__ == "__main__":
#     extractor = TableExtractor("./data/apple-sec-filing.pdf")
#     tables = extractor.extract_tables()

#     extractor.save_json("tables.json")
