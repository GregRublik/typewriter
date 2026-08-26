import json
from config import types
import requests

class TypeWriterService:

    @staticmethod
    def generate_prompt(text_document):
        return f"""
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

    def run(self, text_document):

        prompt = self.generate_prompt(text_document)

        response = requests.post(
            "http://172.17.10.143:8080/completion",
            headers={"Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "n_predict": 50
            }
        )

        return response.json()

typewriter_service = TypeWriterService()
