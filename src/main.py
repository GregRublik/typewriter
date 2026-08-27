from fastapi import FastAPI, UploadFile, File
import uvicorn
import tempfile
import os
import json

from services.typewriter import typewriter_service

from config import settings

if settings.ocr_engine == "paddle":
    from services.ocr import PaddleOCRService

    ocr_service = PaddleOCRService()
else:
    from services.ocr_tesseract import TesseractOCRService

    ocr_service = TesseractOCRService()


app = FastAPI()


@app.post("/analyse")
async def ocr(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        text = ocr_service.run(temp_file_path)

        result = typewriter_service.run(text)

        try:
            res = json.loads(result["content"])
        except Exception:
            res = result["content"]
        return res
    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)