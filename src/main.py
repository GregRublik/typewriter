from fastapi import FastAPI, UploadFile, File, Response
import uvicorn
import tempfile
import os
import json
from pdf2image import convert_from_bytes
from io import BytesIO

from services.typewriter import typewriter_service, TypeWriterError

from config import settings

if settings.ocr_engine == "paddle":
    from services.ocr import PaddleOCRService

    ocr_service = PaddleOCRService()
else:
    from services.ocr_tesseract import TesseractOCRService

    ocr_service = TesseractOCRService()


app = FastAPI()

@app.post("/pdf_to_jpg")
def pdf_to_jpg(file: UploadFile = File(...)):
    # обычный def — FastAPI выполнит обработчик в threadpool, convert_from_bytes не заблокирует event loop
    pdf = file.file.read()
    pages = convert_from_bytes(pdf, dpi=150)
    if not pages:
        return {"error": "PDF is empty"}
    output = BytesIO()
    pages[0].save(output, format="JPEG", quality=90)
    return Response(
        content=output.getvalue(),
        media_type="image/jpeg",
        headers={"Content-Disposition": 'inline; filename="page-1.jpg"'}
    )

@app.post("/analyse")
def ocr(file: UploadFile = File(...)):
    # обычный def — OCR и синхронный requests в typewriter не должны останавливать event loop
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = file.file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        text = ocr_service.run(temp_file_path)

        try:
            result = typewriter_service.run(text)
        except TypeWriterError as e:
            # LLM недоступна даже после повторов — отдаём понятную ошибку вместо тела ответа прокси
            return {"success": False, "error": str(e), "retry_later": True}

        res = result

        try:
            res = json.loads(res["choices"][0]["message"]["content"])
            success = True
        except Exception:
            try:

                res = result["choices"][0]["message"]["content"]
                success = False
            except Exception:
                success = False
                return {"success": success, "result": result}
        return {"success": success, "result": res}
    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
