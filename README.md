# pdf-to-type-document

OCR + классификация типа документа (сертификаты, декларации и т.п.) через `POST /analyse`.

## Стек

- **FastAPI** — эндпоинт `POST /analyse`, принимает PDF или изображение
- **OCR** — два движка на выбор (см. `APP_OCR_ENGINE`):
  - `tesseract` (по умолчанию) — лёгкий, ~0.5 ГБ пика RAM
  - `paddle` — PP-OCRv5, лучше на фото под углом, но ~3.5 ГБ пика RAM
- **LLM-сервис** (`typewriter`) — классификация типа документа

## Настройка (.env)

| Переменная | Описание |
|---|---|
| `APP_HOST` / `APP_PORT` | адрес приложения |
| `APP_OCR_ENGINE` | `tesseract` или `paddle` |
| `LLM_HOST` / `LLM_PORT` | адрес LLM-сервиса классификации |

## Установка на сервере

Для tesseract-движка нужен системный бинарник и русские языковые данные:

```bash
sudo apt install tesseract-ocr tesseract-ocr-rus
uv sync
python src/main.py
```

Paddle-движок (`APP_OCR_ENGINE=paddle`) требует сервер с 4+ ГБ RAM или адекватным swap.

## Сравнение качества движков

```bash
python scripts/compare_ocr.py documents/*.pdf            # оба движка
python scripts/compare_ocr.py --engine tesseract documents/*.pdf
```

Результаты сохраняются в `texts/<имя файла>.<движок>.txt`, в консоль печатается
количество символов, время и пик RAM.
