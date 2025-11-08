from table_extractor import TableExtractor
from ocr_processor import OCRProcessor
from json_combiner import JSONCombiner
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Path to input PDF file")
    parser.add_argument("--output", type=str, help="Path to output JSON file", default="combined-output.json")
    args = parser.parse_args()

    extractor = TableExtractor(args.input)
    extractor.extract_tables()

    table_output_path = "./tmp/table-output.json"
    ocr_output_path = "./tmp/ocr-output.json"

    extractor.save_json(table_output_path)

    ocr_processor = OCRProcessor(
        pdf_path=args.input,
        output_json=ocr_output_path,
        temp_dir='./tmp/'
    )

    result = ocr_processor.process()
    ocr_processor.cleanup()

    combiner = JSONCombiner()
    combiner.load_and_combine(table_output_path, ocr_output_path)
    combiner.save_combined(args.output, minify=True)
