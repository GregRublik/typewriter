import json
from config import types, standards, settings
import requests

class TypeWriterService:

    @staticmethod
    def generate_prompt(text_document):
        return f"""
        Определи тип и стандарт документа а также страну стандарта.
        Возможные типы:
        {json.dumps(types, ensure_ascii=False)}
        Возможные стандарты:
        {json.dumps(standards, ensure_ascii=False)}
        Документ:
        {text_document}
        Формат ответа:
        {{"name": "название типа", "value": "значение типа", "standard": "EAEU", "country": "alpha-2 код страны" }}
        Верни ТОЛЬКО валидный JSON без markdown и дополнительного текста.
        Ответ:
        """

    def run(self, text_document):

        prompt = self.generate_prompt(text_document)

        response = requests.post(
            f"http://{settings.llm.host}:{settings.llm.port}/completion",
            headers={"Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "n_predict": 50
            }
        )

        return response.json()

typewriter_service = TypeWriterService()
