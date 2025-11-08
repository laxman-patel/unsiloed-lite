import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import fitz
import json
import os

class OCRProcessor:

    def __init__(self, pdf_path, output_json='ocr-output.json', temp_dir='./tmp/', dpi=300):

        self.pdf_path = pdf_path
        self.output_json = output_json
        self.temp_dir = temp_dir
        self.dpi = dpi
        self.text_by_page = []
        self.images = []

        os.makedirs(self.temp_dir, exist_ok=True)

    def extract_text(self):

        pages = convert_from_path(self.pdf_path, dpi=self.dpi)
        self.text_by_page = []

        for i, page in enumerate(pages):
            img_file = f'{self.temp_dir}page_{i+1}.png'
            page.save(img_file, 'PNG')
            text = pytesseract.image_to_string(Image.open(img_file))
            self.text_by_page.append({
                'page': i + 1,
                'text': text.strip()
            })

        return self.text_by_page

    def extract_images(self):

        doc = fitz.open(self.pdf_path)
        self.images = []

        for page_number in range(len(doc)):
            for img_index, img in enumerate(doc.get_page_images(page_number)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image['image']
                img_ext = base_image['ext']

                img_filename = f'{self.temp_dir}page_{page_number+1}_img_{img_index+1}.{img_ext}'

                with open(img_filename, 'wb') as f:
                    f.write(image_bytes)

                self.images.append({
                    'page': page_number + 1,
                    'img_file': img_filename
                })

        doc.close()
        return self.images

    def save_to_json(self):

        result = {
            'text_by_page': self.text_by_page,
            'images': self.images
        }

        with open(self.output_json, 'w') as f:
            json.dump(result, f, indent=2)

        print(f'Saved extracted data to {self.output_json}')
        return self.output_json

    def process(self):

        print(f'Processing PDF: {self.pdf_path}')

        print('Extracting text...')
        self.extract_text()

        print('Extracting images...')
        self.extract_images()

        self.save_to_json()

        return {
            'text_by_page': self.text_by_page,
            'images': self.images
        }

    def cleanup(self):

        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f'Cleaned up temporary directory: {self.temp_dir}')


# usage
# if __name__ == '__main__':
#     processor = OCRProcessor(
#         pdf_path='./data/apple-sec-filing.pdf',
#         output_json='ocr-output.json',
#         temp_dir='./tmp_imgs/'
#     )

#     result = processor.process()

#     processor.cleanup()
