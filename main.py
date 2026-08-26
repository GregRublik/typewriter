import os
import requests
import json

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="ru"
)


for doc in os.listdir("documents/"):
    result = ocr.predict(f"documents/{doc}")

    text = []

    for res in result:
        text.extend(res["rec_texts"])

    text_document = "\n".join(text)

    prompt = f"""
    Определи тип документа.

    Возможные типы:
    {json.dumps(types, ensure_ascii=False)}

    Документ:
    {text_document}
    
    Формат ответа:
    {{"name": "название типа", "value": "значение типа"}}

    Верни ТОЛЬКО валидный JSON без markdown и дополнительного текста.

    Ответ:
    """

    response = requests.post(
        "http://172.17.10.143:8080/completion",
        headers={"Content-Type": "application/json"},
        json={
            "prompt": prompt,
            "n_predict": 50
        }
    )

    result = response.json()

    # print(result["content"])

    # print("CONTENT:")
    # print(repr(result["content"]))
    # print("END CONTENT")

    # parsed = json.loads(result["content"])
    # print(parsed)

    # break