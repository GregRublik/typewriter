"""Сравнение качества OCR: Tesseract vs PaddleOCR.

Примеры:
    python scripts/compare_ocr.py documents/*.pdf              # оба движка
    python scripts/compare_ocr.py --engine tesseract documents/*.pdf
    python scripts/compare_ocr.py --engine paddle documents/Сертификат.pdf

Paddle-движку нужно ~3.5 ГБ RAM — запускайте его на машине с памятью
(например aiubuntu), tesseract работает где угодно.

Результаты сохраняются в texts/<имя файла>.<движок>.txt
"""

import argparse
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from services.ocr_tesseract import TesseractOCRService  # noqa: E402


def peak_mb() -> float:
    """Пик RSS процесса. Нарастающий максимум — для чистого замера
    запускайте движки по отдельности через --engine."""
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw / (1024 * 1024) if sys.platform == "darwin" else raw / 1024


def run_engine(name: str, service, file_path: Path) -> str:
    t0 = time.time()
    text = service.run(str(file_path))
    elapsed = time.time() - t0

    print(f"\n=== {name} | {file_path.name} ===")
    print(f"символов: {len(text)}, время: {elapsed:.1f}с, пик RSS: {peak_mb():.0f} МБ")
    print(text[:1500])
    if len(text) > 1500:
        print("... [обрезано, полный текст в файле]")

    out_dir = Path(__file__).resolve().parent.parent / "texts"
    out_path = out_dir / f"{file_path.stem}.{name}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"сохранено: {out_path}")

    return text


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("files", nargs="+", help="PDF или изображения")
    parser.add_argument(
        "--engine",
        choices=["tesseract", "paddle", "both"],
        default="both",
        help="какой движок запускать (по умолчанию both)",
    )
    args = parser.parse_args()

    engines = {}
    if args.engine in ("tesseract", "both"):
        engines["tesseract"] = TesseractOCRService()
    if args.engine in ("paddle", "both"):
        from services.ocr import PaddleOCRService  # noqa: E402

        engines["paddle"] = PaddleOCRService()

    for raw_path in args.files:
        file_path = Path(raw_path)
        for name, service in engines.items():
            try:
                run_engine(name, service, file_path)
            except Exception as exc:
                print(f"\n=== {name} | {file_path.name}: ОШИБКА: {exc}")


if __name__ == "__main__":
    main()
