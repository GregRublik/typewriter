from paddleocr import PaddleOCR


class OCRService:
    def __init__(self):
        self.ocr = PaddleOCR(lang="ru", enable_mkldnn=False)

    def run(self, document_path: str) -> str:
        result = self.ocr.predict(document_path)

        text = []

        for res in result:
            text.extend(res["rec_texts"])

        return "\n".join(text)


ocr_service = OCRService()