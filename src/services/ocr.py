class PaddleOCRService:
    """OCR на PaddleOCR (PP-OCRv5). Тяжёлый движок: ~3.5 ГБ пика RAM.

    Модели грузятся лениво при первом вызове run(),
    чтобы импорт модуля не тянул paddle-рантайм в память.
    """

    def __init__(self):
        self._ocr = None

    def run(self, document_path: str) -> str:
        if self._ocr is None:
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(
                lang="ru",
                enable_mkldnn=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                cpu_threads=2,
            )

        result = self._ocr.predict(document_path)

        text = []

        for res in result:
            text.extend(res["rec_texts"])

        return "\n".join(text)
