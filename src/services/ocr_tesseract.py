import cv2
import numpy as np
import pymupdf as fitz
import pytesseract


class TesseractOCRService:
    """OCR на Tesseract: рендер PDF -> предобработка -> распознавание.

    Лёгкая альтернатива paddle-движку (~0.5 ГБ пика вместо ~3.5 ГБ).
    """

    PDF_DPI = 300

    def run(self, document_path: str) -> str:
        if document_path.lower().endswith(".pdf"):
            pages = self._render_pdf(document_path)
        else:
            pages = [self._read_image(document_path)]

        texts = []
        for page in pages:
            processed = self._preprocess(page)
            page_text = pytesseract.image_to_string(processed, lang="rus+eng").strip()
            if page_text:
                texts.append(page_text)

        return "\n".join(texts)

    @staticmethod
    def _read_image(path: str) -> np.ndarray:
        # cv2.imread не дружит с кириллицей в пути — читаем через numpy
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Не удалось прочитать изображение: {path}")
        return img

    def _render_pdf(self, path: str) -> list[np.ndarray]:
        pages = []
        with fitz.open(path) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=self.PDF_DPI)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, pix.n
                )
                if pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                elif pix.n == 1:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                pages.append(img)
        return pages

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        # маленькие изображения (фото с телефона) увеличиваем — tesseract любит крупный текст
        h, w = img.shape[:2]
        if max(h, w) < 2000:
            scale = 2 if max(h, w) < 1000 else 1.5
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        # адаптивный порог: работает и на сканах, и на фото с неравномерным освещением
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 15
        )
