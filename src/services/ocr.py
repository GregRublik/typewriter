from paddleocr import PaddleOCR


class OCRService:
    def __init__(self):
        self.ocr = PaddleOCR(
            lang="ru",
            enable_mkldnn=False,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            cpu_threads=2,
        )

    def run(self, document_path: str) -> str:
        result = self.ocr.predict(document_path)

        text = []

        for res in result:
            text.extend(res["rec_texts"])

        res = "\n".join(text)
        print(res)

        return res


ocr_service = OCRService()